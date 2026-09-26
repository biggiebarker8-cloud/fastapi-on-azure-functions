from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

from .actor_context import get_current_actor
from .models import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRequestCreate,
    Asset,
    AssistantIdentity,
    Character,
    CharacterCreate,
    ImageEditRequest,
    KnowledgeBaseEntry,
    LearningEvent,
    LearningEventCreate,
    LearningPolicyUpdate,
    MerchDesignCreate,
    NonLinearThoughtRequest,
    Playbook,
    PlaybookCreate,
    PreferenceUpdate,
    Plugin,
    PluginDraftCreate,
    PluginKillRequest,
    PluginRollbackRequest,
    PluginToggleRequest,
    PluginVersionUpdate,
    Skill,
    SkillCreate,
    SkillToggleRequest,
    Story,
    StoryCreate,
    StructuredThoughtResponse,
    Universe,
    UniverseCreate,
    UserPreferenceProfile,
)
from .moderation import moderate_text
from .storage import InMemoryStore

ALLOWED_PLUGIN_CAPABILITIES = {
    "read_data",
    "write_data",
    "run_workflow",
    "generate_content",
    "analyze_metrics",
    "use_external_api",
}


class KarmaService:
    def __init__(self, store: InMemoryStore, identity: AssistantIdentity) -> None:
        self.store = store
        self.identity = identity

    def set_identity(
        self,
        name: str | None = None,
        tone: str | None = None,
        lore: str | None = None,
    ) -> AssistantIdentity:
        with self.store.lock:
            if name is not None:
                self.identity.name = name
            if tone is not None:
                self.identity.tone = tone
            if lore is not None:
                self.identity.lore = lore
        return self.identity

    def update_preferences(self, payload: PreferenceUpdate) -> UserPreferenceProfile:
        with self.store.lock:
            self.store.preferences.likes = payload.likes
            self.store.preferences.dislikes = payload.dislikes
            self.store.preferences.output_preferences = payload.output_preferences
            self.store.preferences.thinking_profile = payload.thinking_profile
            self.store.preferences.desired_assistant_behavior = payload.desired_assistant_behavior
            self.store.preferences.updated_at = datetime.now(timezone.utc).isoformat()
        return self.store.preferences

    def structure_non_linear_input(self, payload: NonLinearThoughtRequest) -> StructuredThoughtResponse:
        check = moderate_text(f"{payload.raw_input} {payload.goal}")
        if not check.allowed:
            raise HTTPException(status_code=400, detail=check.reason)

        phases = [
            "Define one concrete outcome.",
            "Split the idea into modules and dependencies.",
            "Prioritize by impact and implementation risk.",
            "Execute highest-priority slice and re-evaluate.",
        ]
        if payload.constraints:
            phases.append("Adjust scope to satisfy listed constraints.")

        infeasible_markers = {"all permissions", "doesn't forget anything", "self install all plugins"}
        lowered = payload.raw_input.lower()
        infeasible = any(marker in lowered for marker in infeasible_markers)
        feasibility = "won't_work_without_changes" if infeasible else "works"
        feedback = (
            "Straight answer: this won't work as-is; scope or permissions must change."
            if infeasible
            else "Straight answer: this can work with phased implementation."
        )
        assumptions = [
            "Preference memory is profile-based and explicitly editable.",
            "Output style should stay blunt, caring, and structured.",
        ]
        return StructuredThoughtResponse(
            summary=payload.goal or "Structured action plan from non-linear input.",
            assumptions=assumptions + payload.constraints,
            phases=phases,
            feasibility=feasibility,
            straight_feedback=feedback,
        )

    def create_universe(self, payload: UniverseCreate) -> Universe:
        check = moderate_text(f"{payload.name} {payload.canon} {payload.timeline}")
        if not check.allowed:
            raise HTTPException(status_code=400, detail=check.reason)
        universe = Universe(**payload.model_dump())
        return self.store.add_universe(universe)

    def create_character(self, payload: CharacterCreate) -> Character:
        with self.store.lock:
            if payload.universe_id not in self.store.universes:
                raise HTTPException(status_code=404, detail="Universe not found.")
            check = moderate_text(f"{payload.name} {payload.backstory} {payload.lore_notes}")
            if not check.allowed:
                raise HTTPException(status_code=400, detail=check.reason)
            character = Character(**payload.model_dump())
            character = self.store.add_character(character)
            self._add_asset(
                "character",
                character.id,
                character.universe_id,
                {"name": character.name},
                initial_summary=f"Character created: {character.name}",
            )
            return character

    def create_story(self, payload: StoryCreate) -> Story:
        with self.store.lock:
            if payload.universe_id not in self.store.universes:
                raise HTTPException(status_code=404, detail="Universe not found.")
            check = moderate_text(f"{payload.title} {payload.arc} {payload.backstory} {payload.lore}")
            if not check.allowed:
                raise HTTPException(status_code=400, detail=check.reason)

            continuity_notes: list[str] = []
            validated_crossover_universe_ids: set[str] = set()
            for character_id in payload.character_ids:
                character = self.store.characters.get(character_id)
                if not character:
                    raise HTTPException(status_code=404, detail=f"Character not found: {character_id}")

                if character.universe_id != payload.universe_id:
                    if payload.allow_crossover and character.universe_id in payload.crossover_universe_ids:
                        validated_crossover_universe_ids.add(character.universe_id)
                        continuity_notes.append(
                            f"Crossover allowed for character {character_id} from universe {character.universe_id}."
                        )
                    else:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Continuity violation for character {character_id}; enable crossover and include source universe.",
                        )

            story_payload = payload.model_dump(exclude={"allow_crossover"})
            if not payload.allow_crossover:
                story_payload["crossover_universe_ids"] = []
            else:
                story_payload["crossover_universe_ids"] = sorted(validated_crossover_universe_ids)
            story = Story(**story_payload, continuity_notes=continuity_notes)
            story = self.store.add_story(story)
            self._add_asset(
                "story",
                story.id,
                story.universe_id,
                {"title": story.title},
                initial_summary=f"Story created: {story.title}",
            )
            return story

    def create_merch_design(self, payload: MerchDesignCreate) -> Asset:
        with self.store.lock:
            if payload.universe_id not in self.store.universes:
                raise HTTPException(status_code=404, detail="Universe not found.")
            check = moderate_text(payload.theme_prompt)
            if not check.allowed:
                raise HTTPException(status_code=400, detail=check.reason)

            summary = (
                f"{payload.product_type} design in {payload.print_area} area; "
                f"{len(payload.variants)} variant(s), exports={payload.export_formats}"
            )
            asset = self._add_asset(
                "merch_design",
                reference_id=f"{payload.product_type}:{payload.universe_id}",
                universe_id=payload.universe_id,
                metadata=payload.model_dump(),
                initial_summary=summary,
            )
            return self.store.assets[asset.id]

    def edit_image(self, payload: ImageEditRequest) -> Asset:
        with self.store.lock:
            if payload.universe_id not in self.store.universes:
                raise HTTPException(status_code=404, detail="Universe not found.")
            source = self.store.assets.get(payload.source_asset_id)
            if not source:
                raise HTTPException(status_code=404, detail="Source asset not found.")
            if source.universe_id != payload.universe_id:
                raise HTTPException(status_code=400, detail="Source asset universe mismatch.")

            check = moderate_text(payload.instructions)
            if not check.allowed:
                raise HTTPException(status_code=400, detail=check.reason)

            asset = self._add_asset(
                "image_edit",
                reference_id=payload.source_asset_id,
                universe_id=payload.universe_id,
                metadata=payload.model_dump(),
                initial_summary=f"Image edit requested via {payload.operation}",
            )
            return self.store.assets[asset.id]

    def restore_asset_version(self, asset_id: str, version: int) -> Asset:
        with self.store.lock:
            asset = self.store.assets.get(asset_id)
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found.")
            version_map = {item.version: item for item in asset.versions}
            selected_version = version_map.get(version)
            if not selected_version:
                raise HTTPException(status_code=404, detail="Version not found.")
            current_version_before_restore = asset.current_version
            self.store.append_asset_version(
                asset_id,
                f"Checkpoint before restore to version {version}",
                metadata_snapshot=dict(asset.metadata),
                reference_id_snapshot=asset.reference_id,
                source_version=current_version_before_restore,
            )
            asset.metadata = dict(selected_version.metadata_snapshot)
            if selected_version.reference_id_snapshot is not None:
                asset.reference_id = selected_version.reference_id_snapshot
            self.store.append_asset_version(
                asset_id,
                f"Restored from version {version}",
                metadata_snapshot=dict(asset.metadata),
                reference_id_snapshot=asset.reference_id,
                source_version=version,
                restored_from_version=version,
            )
            return self.store.assets[asset_id]

    def list_knowledge_bases(self) -> list[KnowledgeBaseEntry]:
        with self.store.lock:
            return list(self.store.knowledge_bases.values())

    def get_knowledge_base(self, knowledge_base_id: str) -> KnowledgeBaseEntry:
        with self.store.lock:
            knowledge_base = self.store.knowledge_bases.get(knowledge_base_id)
            if knowledge_base:
                return knowledge_base
            aliases = {alias.lower(): item for item in self.store.knowledge_bases.values() for alias in item.aliases}
            alias_match = aliases.get(knowledge_base_id.lower())
            if alias_match:
                return alias_match
        raise HTTPException(status_code=404, detail="Knowledge base not found.")

    def draft_plugin(self, payload: PluginDraftCreate) -> Plugin:
        self._validate_capabilities(payload.capabilities)
        check = moderate_text(f"{payload.name} {payload.owner}")
        if not check.allowed:
            raise HTTPException(status_code=400, detail=check.reason)

        plugin = Plugin(**payload.model_dump())
        plugin.secret_scope = f"plugin/{plugin.id}/vault"
        return self.store.add_plugin(plugin)

    def validate_plugin(self, plugin_id: str) -> Plugin:
        plugin = self._get_plugin_or_404(plugin_id)
        with self.store.lock:
            plugin.validation_notes = [
                "Capability allowlist validated.",
                "Scoped secret vault isolation assigned.",
                "Sandbox staging required before publish.",
            ]
            plugin.lifecycle_state = "validated"
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return plugin

    def stage_plugin(self, plugin_id: str) -> Plugin:
        plugin = self._get_plugin_or_404(plugin_id)
        if plugin.lifecycle_state not in {"validated", "disabled", "rolled_back"}:
            raise HTTPException(status_code=400, detail="Plugin must be validated before staging.")
        with self.store.lock:
            plugin.lifecycle_state = "staged"
            plugin.health_status = "healthy"
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return plugin

    def submit_plugin_for_approval(
        self,
        plugin_id: str,
        reason: str = "",
    ) -> ApprovalRequest:
        plugin = self._get_plugin_or_404(plugin_id)
        if plugin.lifecycle_state != "staged":
            raise HTTPException(status_code=400, detail="Plugin must pass staging before approval request.")
        approval = self.create_approval_request(
            ApprovalRequestCreate(
                action_type="plugin_publish",
                target_type="plugin",
                target_id=plugin_id,
                requested_by=self._current_actor(),
                reason=reason or "Promote plugin from staging to production.",
                required_owner_approval=True,
            )
        )
        with self.store.lock:
            plugin.pre_approval_lifecycle_state = plugin.lifecycle_state
            plugin.lifecycle_state = "pending_approval"
            plugin.approval_request_id = approval.id
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return approval

    def update_plugin_version(self, plugin_id: str, payload: PluginVersionUpdate) -> ApprovalRequest:
        plugin = self._get_plugin_or_404(plugin_id)
        if plugin.lifecycle_state not in {"enabled", "rolled_back"}:
            raise HTTPException(status_code=400, detail="Plugin version updates require an already approved live or rolled-back plugin.")
        approval = self.create_approval_request(
            ApprovalRequestCreate(
                action_type="plugin_update",
                target_type="plugin",
                target_id=plugin.id,
                requested_by=self._current_actor(),
                reason=f"Approve plugin version {payload.version}.",
                required_owner_approval=True,
            )
        )
        with self.store.lock:
            plugin.pending_version = payload.version
            plugin.pre_approval_lifecycle_state = plugin.lifecycle_state
            plugin.lifecycle_state = "pending_approval"
            plugin.approval_request_id = approval.id
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return approval

    def toggle_plugin(self, plugin_id: str, payload: PluginToggleRequest) -> Plugin:
        plugin = self._get_plugin_or_404(plugin_id)
        if plugin.lifecycle_state == "killed" and payload.enabled:
            raise HTTPException(status_code=400, detail="Killed plugins must be rolled back or rebuilt before enabling.")
        if payload.enabled:
            if plugin.lifecycle_state == "pending_approval":
                raise HTTPException(status_code=403, detail="Plugin enablement is blocked while an approval decision is pending.")
            self._get_required_approved_plugin_approval(plugin)

        with self.store.lock:
            plugin.lifecycle_state = "enabled" if payload.enabled else "disabled"
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return plugin

    def rollback_plugin(self, plugin_id: str, payload: PluginRollbackRequest) -> Plugin:
        plugin = self._get_plugin_or_404(plugin_id)
        actor = self._current_actor()
        with self.store.lock:
            plugin.lifecycle_state = "rolled_back"
            plugin.rollback_history.append(f"{actor}: {payload.reason}")
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return plugin

    def kill_plugin(self, plugin_id: str, payload: PluginKillRequest) -> Plugin:
        plugin = self._get_plugin_or_404(plugin_id)
        actor = self._current_actor()
        with self.store.lock:
            plugin.lifecycle_state = "killed"
            plugin.health_status = "unhealthy"
            plugin.rollback_history.append(f"{actor}: kill switch - {payload.reason}")
            plugin.updated_at = datetime.now(timezone.utc).isoformat()
        return plugin

    def create_skill(self, payload: SkillCreate) -> Skill:
        self._validate_capabilities(payload.capabilities)
        if payload.plugin_id and payload.plugin_id not in self.store.plugins:
            raise HTTPException(status_code=404, detail="Plugin not found.")

        skill = Skill(**payload.model_dump())
        if payload.external_api_access:
            approval = self.create_approval_request(
                ApprovalRequestCreate(
                    action_type="skill_external_access",
                    target_type="skill",
                    target_id=skill.id,
                    requested_by=self._current_actor(),
                    reason="External API access requested for skill.",
                    required_owner_approval=True,
                )
            )
            skill.approval_request_id = approval.id
            skill.enabled = False
        else:
            skill.enabled = True
        return self.store.add_skill(skill)

    def toggle_skill(self, skill_id: str, payload: SkillToggleRequest) -> Skill:
        with self.store.lock:
            skill = self.store.skills.get(skill_id)
            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found.")
            if payload.enabled and skill.external_api_access:
                approval = self.store.approvals.get(skill.approval_request_id) if skill.approval_request_id else None
                if not approval or approval.status != "approved":
                    raise HTTPException(status_code=403, detail="Skill enablement requires approved external access.")
            skill.enabled = payload.enabled
            skill.updated_at = datetime.now(timezone.utc).isoformat()
            return skill

    def create_approval_request(self, payload: ApprovalRequestCreate) -> ApprovalRequest:
        approval_payload = payload.model_dump()
        approval_payload["requested_by"] = self._current_actor()
        if (
            approval_payload["action_type"] in {"plugin_publish", "plugin_update", "skill_external_access"}
            or (
                approval_payload["action_type"] == "learning_rule_change"
                and approval_payload["target_type"] in {"playbook", "learning_policy"}
            )
        ):
            approval_payload["required_owner_approval"] = True
        approval = ApprovalRequest(**approval_payload)
        return self.store.add_approval(approval)

    def decide_approval(self, approval_id: str, payload: ApprovalDecision) -> ApprovalRequest:
        with self.store.lock:
            approval = self.store.approvals.get(approval_id)
            if not approval:
                raise HTTPException(status_code=404, detail="Approval request not found.")
            if approval.status != "pending":
                raise HTTPException(status_code=400, detail="Approval request already decided.")

            approval.status = "approved" if payload.approve else "rejected"
            approval.decided_by = self._current_actor() if approval.required_owner_approval else payload.decided_by
            approval.decision_notes = payload.notes
            approval.decided_at = datetime.now(timezone.utc).isoformat()

        if approval.target_type == "plugin":
            plugin = self.store.plugins.get(approval.target_id)
            if plugin and plugin.approval_request_id == approval.id:
                with self.store.lock:
                    if approval.action_type == "plugin_publish":
                        plugin.lifecycle_state = "enabled" if payload.approve else (plugin.pre_approval_lifecycle_state or "staged")
                        plugin.pending_version = None
                        plugin.approval_request_id = (
                            approval.id
                            if payload.approve
                            else self._latest_approved_plugin_approval_id(plugin.id, exclude_approval_id=approval.id)
                        )
                    elif approval.action_type == "plugin_update":
                        if payload.approve and plugin.pending_version is not None:
                            plugin.version = plugin.pending_version
                            plugin.lifecycle_state = "enabled"
                        else:
                            plugin.lifecycle_state = plugin.pre_approval_lifecycle_state or plugin.lifecycle_state
                        plugin.pending_version = None
                        plugin.approval_request_id = (
                            approval.id
                            if payload.approve
                            else self._latest_approved_plugin_approval_id(plugin.id, exclude_approval_id=approval.id)
                        )
                    plugin.pre_approval_lifecycle_state = None
                    plugin.updated_at = datetime.now(timezone.utc).isoformat()
        elif approval.target_type == "skill":
            skill = self.store.skills.get(approval.target_id)
            if (
                skill
                and payload.approve
                and approval.action_type == "skill_external_access"
                and skill.approval_request_id == approval.id
            ):
                with self.store.lock:
                    skill.enabled = True
                    skill.updated_at = datetime.now(timezone.utc).isoformat()
        elif approval.target_type == "playbook":
            playbook = self.store.playbooks.get(approval.target_id)
            if playbook:
                with self.store.lock:
                    playbook.status = "active" if payload.approve else "rejected"
                    playbook.updated_at = datetime.now(timezone.utc).isoformat()
        return approval

    def record_learning_event(self, payload: LearningEventCreate) -> dict:
        check = moderate_text(f"{payload.source} {payload.outcome} {payload.feedback}")
        if not check.allowed:
            raise HTTPException(status_code=400, detail=check.reason)

        event = LearningEvent(**payload.model_dump())
        self.store.add_learning_event(event)

        suggested_playbook: Playbook | None = None
        if payload.successful and (payload.user_edits or payload.feedback):
            suggested_playbook = self.store.add_playbook(
                Playbook(
                    title=f"Suggested pattern from {payload.source}",
                    trigger=payload.outcome,
                    actions=payload.user_edits or [payload.feedback],
                    risk_level="low",
                    status="draft",
                    requested_by="system",
                )
            )
        return {"event": event, "playbook_suggestion": suggested_playbook}

    def propose_playbook(self, payload: PlaybookCreate) -> Playbook:
        check = moderate_text(f"{payload.title} {payload.trigger} {' '.join(payload.actions)}")
        if not check.allowed:
            raise HTTPException(status_code=400, detail=check.reason)

        playbook = Playbook(**payload.model_dump())
        playbook.requested_by = self._current_actor()
        auto_approve = payload.risk_level == "low" and self.store.learning_policy.auto_approve_low_risk_tuning
        if auto_approve:
            playbook.status = "active"
        else:
            playbook.status = "pending_approval"
            approval = self.create_approval_request(
                ApprovalRequestCreate(
                    action_type="learning_rule_change",
                    target_type="playbook",
                    target_id=playbook.id,
                    requested_by=self._current_actor(),
                    reason="Approve playbook activation.",
                    required_owner_approval=True,
                )
            )
            playbook.approval_request_id = approval.id
        return self.store.add_playbook(playbook)

    def request_learning_policy_change(
        self,
        reason: str = "",
    ) -> ApprovalRequest:
        return self.create_approval_request(
            ApprovalRequestCreate(
                action_type="learning_rule_change",
                target_type="learning_policy",
                target_id="learning_policy",
                requested_by=self._current_actor(),
                reason=reason or "Approve learning policy change.",
                required_owner_approval=True,
            )
        )

    def update_learning_policy(self, payload: LearningPolicyUpdate) -> dict:
        if payload.approval_request_id is None or not self._approval_is_approved(payload.approval_request_id):
            raise HTTPException(status_code=403, detail="Learning policy changes require prior approved request.")

        approval = self.store.approvals.get(payload.approval_request_id)
        if (
            not approval
            or approval.target_type != "learning_policy"
            or approval.action_type != "learning_rule_change"
            or not approval.required_owner_approval
        ):
            raise HTTPException(status_code=400, detail="Approval request does not apply to learning policy.")
        if approval.applied_at is not None:
            raise HTTPException(status_code=400, detail="Approval request has already been applied.")

        with self.store.lock:
            applied_at = datetime.now(timezone.utc).isoformat()
            self.store.learning_policy.auto_approve_low_risk_tuning = payload.auto_approve_low_risk_tuning
            self.store.learning_policy.updated_at = applied_at
            approval.applied_at = applied_at
        return {"learning_policy": self.store.learning_policy, "applied_approval_id": payload.approval_request_id}

    def _add_asset(
        self,
        asset_type: str,
        reference_id: str,
        universe_id: str,
        metadata: dict,
        initial_summary: str | None = None,
    ) -> Asset:
        asset = Asset(
            asset_type=asset_type,
            reference_id=reference_id,
            universe_id=universe_id,
            metadata=metadata,
        )
        self.store.add_asset(asset)
        if initial_summary:
            self.store.append_asset_version(
                asset.id,
                initial_summary,
                metadata_snapshot=dict(metadata),
                reference_id_snapshot=reference_id,
            )
        return asset

    def _validate_capabilities(self, capabilities: list[str]) -> None:
        invalid = [capability for capability in capabilities if capability not in ALLOWED_PLUGIN_CAPABILITIES]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported capabilities: {', '.join(sorted(invalid))}.",
            )

    def _get_plugin_or_404(self, plugin_id: str) -> Plugin:
        plugin = self.store.plugins.get(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found.")
        return plugin

    def _approval_is_approved(self, approval_id: str) -> bool:
        approval = self.store.approvals.get(approval_id)
        return bool(approval and approval.status == "approved")

    def _get_required_approved_plugin_approval(self, plugin: Plugin) -> ApprovalRequest:
        approval = None
        if plugin.approval_request_id:
            candidate = self.store.approvals.get(plugin.approval_request_id)
            if (
                candidate
                and candidate.status == "approved"
                and candidate.required_owner_approval
                and candidate.target_type == "plugin"
                and candidate.target_id == plugin.id
                and candidate.action_type in {"plugin_publish", "plugin_update"}
            ):
                approval = candidate
        if approval is None:
            latest_approval_id = self._latest_approved_plugin_approval_id(plugin.id)
            approval = self.store.approvals.get(latest_approval_id) if latest_approval_id else None
        if approval is None:
            raise HTTPException(status_code=403, detail="Plugin enablement requires approved request.")
        return approval

    def _current_actor(self) -> str:
        actor = get_current_actor()
        if not actor:
            raise HTTPException(status_code=403, detail="Owner-gated actions require authenticated actor context.")
        return actor

    def _latest_approved_plugin_approval_id(
        self,
        plugin_id: str,
        exclude_approval_id: str | None = None,
    ) -> str | None:
        latest_approval_id: str | None = None
        latest_approval_sort_key = ""
        for approval in self.store.approvals.values():
            if approval.id == exclude_approval_id:
                continue
            if approval.status != "approved":
                continue
            if not approval.required_owner_approval:
                continue
            if approval.target_type != "plugin" or approval.target_id != plugin_id:
                continue
            if approval.action_type not in {"plugin_publish", "plugin_update"}:
                continue
            sort_key = approval.decided_at or approval.created_at
            if sort_key >= latest_approval_sort_key:
                latest_approval_id = approval.id
                latest_approval_sort_key = sort_key
        return latest_approval_id
