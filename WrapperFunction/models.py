from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AssistantIdentity(BaseModel):
    name: str = "Karma"
    tone: str
    lore: str = ""
    authority_rule: str = "User is the final decision-maker; assistant advises and executes."


class IdentityUpdate(BaseModel):
    name: str | None = None
    tone: str | None = None
    lore: str | None = None


class UniverseCreate(BaseModel):
    name: str
    canon: str = ""
    timeline: str = ""
    style_settings: dict = Field(default_factory=dict)


class Universe(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("uni"))
    name: str
    canon: str = ""
    timeline: str = ""
    style_settings: dict = Field(default_factory=dict)
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class CharacterCreate(BaseModel):
    universe_id: str
    name: str
    backstory: str = ""
    lore_notes: str = ""
    traits: list[str] = Field(default_factory=list)


class Character(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("char"))
    universe_id: str
    name: str
    backstory: str = ""
    lore_notes: str = ""
    traits: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)


class StoryCreate(BaseModel):
    universe_id: str
    title: str
    arc: str
    backstory: str = ""
    lore: str = ""
    character_ids: list[str] = Field(default_factory=list)
    crossover_universe_ids: list[str] = Field(default_factory=list)
    allow_crossover: bool = False


class Story(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("story"))
    universe_id: str
    title: str
    arc: str
    backstory: str = ""
    lore: str = ""
    character_ids: list[str] = Field(default_factory=list)
    crossover_universe_ids: list[str] = Field(default_factory=list)
    continuity_notes: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)


class MerchDesignCreate(BaseModel):
    universe_id: str
    product_type: Literal["hoodie", "tshirt"]
    theme_prompt: str
    print_area: Literal["front", "back", "sleeve", "full"]
    variants: list[str] = Field(default_factory=list)
    export_formats: list[str] = Field(default_factory=lambda: ["png"])

    @model_validator(mode="after")
    def validate_print_area(self) -> "MerchDesignCreate":
        invalid_combo = self.print_area == "sleeve" and self.product_type != "hoodie"
        if invalid_combo:
            raise ValueError("Only hoodie designs support the sleeve print area.")
        return self


class ImageEditRequest(BaseModel):
    universe_id: str
    source_asset_id: str
    operation: Literal[
        "style_transfer",
        "element_replacement",
        "composition_edit",
        "iterative_revision",
    ]
    instructions: str


class AssetVersion(BaseModel):
    version: int
    content_summary: str
    metadata_snapshot: dict = Field(default_factory=dict)
    reference_id_snapshot: str | None = None
    source_version: int | None = None
    restored_from_version: int | None = None
    created_at: str = Field(default_factory=_now_iso)


class Asset(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("asset"))
    universe_id: str
    asset_type: Literal["story", "character", "merch_design", "image_edit"]
    reference_id: str
    metadata: dict = Field(default_factory=dict)
    versions: list[AssetVersion] = Field(default_factory=list)
    current_version: int = 0
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class ModerationResult(BaseModel):
    allowed: bool
    reason: Optional[str] = None


class KnowledgeBaseSection(BaseModel):
    heading: str
    points: list[str] = Field(default_factory=list)


class KnowledgeBaseEntry(BaseModel):
    id: str
    title: str
    summary: str
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    sections: list[KnowledgeBaseSection] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=_now_iso)


class UserPreferenceProfile(BaseModel):
    likes: list[str] = Field(default_factory=list)
    dislikes: list[str] = Field(default_factory=list)
    output_preferences: list[str] = Field(default_factory=list)
    thinking_profile: str = "non-linear"
    desired_assistant_behavior: str = (
        "Straight feedback when ideas are not feasible; user is always the final authority."
    )
    updated_at: str = Field(default_factory=_now_iso)


class PreferenceUpdate(BaseModel):
    likes: list[str] = Field(default_factory=list)
    dislikes: list[str] = Field(default_factory=list)
    output_preferences: list[str] = Field(default_factory=list)
    thinking_profile: str = "non-linear"
    desired_assistant_behavior: str = (
        "Straight feedback when ideas are not feasible; user is always the final authority."
    )


class NonLinearThoughtRequest(BaseModel):
    raw_input: str
    goal: str = ""
    constraints: list[str] = Field(default_factory=list)


class StructuredThoughtResponse(BaseModel):
    summary: str
    assumptions: list[str] = Field(default_factory=list)
    phases: list[str] = Field(default_factory=list)
    feasibility: Literal["works", "won't_work_without_changes"]
    straight_feedback: str


class PluginDraftCreate(BaseModel):
    name: str
    owner: str
    plugin_type: Literal["integration", "automation", "creative", "analytics"]
    version: str = "0.1.0"
    capabilities: list[str] = Field(default_factory=list)
    external_api_access: bool = False
    config: dict[str, Any] = Field(default_factory=dict)


class PluginVersionUpdate(BaseModel):
    version: str
    requested_by: str = "owner"


class PluginToggleRequest(BaseModel):
    enabled: bool
    requested_by: str = "owner"


class Plugin(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("plugin"))
    name: str
    owner: str
    plugin_type: Literal["integration", "automation", "creative", "analytics"]
    version: str = "0.1.0"
    capabilities: list[str] = Field(default_factory=list)
    external_api_access: bool = False
    config: dict[str, Any] = Field(default_factory=dict)
    lifecycle_state: Literal[
        "draft",
        "validated",
        "staged",
        "pending_approval",
        "enabled",
        "disabled",
        "rolled_back",
        "killed",
    ] = "draft"
    health_status: Literal["unknown", "healthy", "unhealthy"] = "unknown"
    validation_notes: list[str] = Field(default_factory=list)
    approval_request_id: str | None = None
    pending_version: str | None = None
    pre_approval_lifecycle_state: Literal[
        "draft",
        "validated",
        "staged",
        "enabled",
        "disabled",
        "rolled_back",
        "killed",
    ] | None = None
    rollback_history: list[str] = Field(default_factory=list)
    secret_scope: str = ""
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class PluginRollbackRequest(BaseModel):
    reason: str = "manual rollback"
    requested_by: str = "owner"


class PluginKillRequest(BaseModel):
    reason: str = "manual kill switch"
    requested_by: str = "owner"


class SkillCreate(BaseModel):
    name: str
    owner: str
    skill_type: Literal["integration", "automation", "creative", "analytics"]
    capabilities: list[str] = Field(default_factory=list)
    plugin_id: str | None = None
    external_api_access: bool = False


class SkillToggleRequest(BaseModel):
    enabled: bool
    requested_by: str = "owner"


class Skill(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("skill"))
    name: str
    owner: str
    skill_type: Literal["integration", "automation", "creative", "analytics"]
    capabilities: list[str] = Field(default_factory=list)
    plugin_id: str | None = None
    external_api_access: bool = False
    enabled: bool = False
    approval_request_id: str | None = None
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class ApprovalRequestCreate(BaseModel):
    action_type: Literal[
        "plugin_install",
        "plugin_update",
        "plugin_publish",
        "skill_external_access",
        "learning_rule_change",
    ]
    target_type: Literal["plugin", "skill", "playbook", "learning_policy"]
    target_id: str
    requested_by: str = "owner"
    reason: str = ""
    required_owner_approval: bool = True


class ApprovalDecision(BaseModel):
    approve: bool
    decided_by: str = "owner"
    notes: str = ""


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("apr"))
    action_type: Literal[
        "plugin_install",
        "plugin_update",
        "plugin_publish",
        "skill_external_access",
        "learning_rule_change",
    ]
    target_type: Literal["plugin", "skill", "playbook", "learning_policy"]
    target_id: str
    requested_by: str = "owner"
    reason: str = ""
    required_owner_approval: bool = True
    status: Literal["pending", "approved", "rejected"] = "pending"
    decided_by: str | None = None
    decision_notes: str = ""
    created_at: str = Field(default_factory=_now_iso)
    decided_at: str | None = None


class LearningEventCreate(BaseModel):
    source: str
    outcome: str
    successful: bool
    feedback: str = ""
    user_edits: list[str] = Field(default_factory=list)


class LearningEvent(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("learn"))
    source: str
    outcome: str
    successful: bool
    feedback: str = ""
    user_edits: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)


class PlaybookCreate(BaseModel):
    title: str
    trigger: str
    actions: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "high"] = "low"
    requested_by: str = "owner"


class Playbook(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("play"))
    title: str
    trigger: str
    actions: list[str] = Field(default_factory=list)
    risk_level: Literal["low", "high"] = "low"
    status: Literal["draft", "pending_approval", "active", "rejected"] = "draft"
    approval_request_id: str | None = None
    requested_by: str = "owner"
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class LearningPolicy(BaseModel):
    auto_approve_low_risk_tuning: bool = False
    updated_at: str = Field(default_factory=_now_iso)


class LearningPolicyUpdate(BaseModel):
    auto_approve_low_risk_tuning: bool
    approval_request_id: str | None = None
