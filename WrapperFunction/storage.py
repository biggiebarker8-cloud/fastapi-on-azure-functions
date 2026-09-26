from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock

from .knowledge_base import load_default_knowledge_bases
from .models import (
    ApprovalRequest,
    Asset,
    AssetVersion,
    Character,
    KnowledgeBaseEntry,
    LearningEvent,
    LearningPolicy,
    Playbook,
    Plugin,
    Skill,
    Story,
    Universe,
    UserPreferenceProfile,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryStore:
    def __init__(self) -> None:
        self.lock = RLock()
        self.universes: dict[str, Universe] = {}
        self.characters: dict[str, Character] = {}
        self.stories: dict[str, Story] = {}
        self.assets: dict[str, Asset] = {}
        self.knowledge_bases: dict[str, KnowledgeBaseEntry] = load_default_knowledge_bases()
        self.preferences: UserPreferenceProfile = UserPreferenceProfile()
        self.plugins: dict[str, Plugin] = {}
        self.skills: dict[str, Skill] = {}
        self.approvals: dict[str, ApprovalRequest] = {}
        self.learning_events: dict[str, LearningEvent] = {}
        self.playbooks: dict[str, Playbook] = {}
        self.learning_policy: LearningPolicy = LearningPolicy()

    def add_universe(self, universe: Universe) -> Universe:
        with self.lock:
            self.universes[universe.id] = universe
        return universe

    def add_character(self, character: Character) -> Character:
        with self.lock:
            self.characters[character.id] = character
        return character

    def add_story(self, story: Story) -> Story:
        with self.lock:
            self.stories[story.id] = story
        return story

    def add_asset(self, asset: Asset) -> Asset:
        with self.lock:
            self.assets[asset.id] = asset
        return asset

    def add_plugin(self, plugin: Plugin) -> Plugin:
        with self.lock:
            self.plugins[plugin.id] = plugin
        return plugin

    def add_skill(self, skill: Skill) -> Skill:
        with self.lock:
            self.skills[skill.id] = skill
        return skill

    def add_approval(self, approval: ApprovalRequest) -> ApprovalRequest:
        with self.lock:
            self.approvals[approval.id] = approval
        return approval

    def add_learning_event(self, event: LearningEvent) -> LearningEvent:
        with self.lock:
            self.learning_events[event.id] = event
        return event

    def add_playbook(self, playbook: Playbook) -> Playbook:
        with self.lock:
            self.playbooks[playbook.id] = playbook
        return playbook

    def append_asset_version(
        self,
        asset_id: str,
        summary: str,
        metadata_snapshot: dict | None = None,
        reference_id_snapshot: str | None = None,
        source_version: int | None = None,
        restored_from_version: int | None = None,
    ) -> Asset:
        with self.lock:
            asset = self.assets[asset_id]
            new_version = asset.current_version + 1
            asset.versions.append(
                AssetVersion(
                    version=new_version,
                    content_summary=summary,
                    metadata_snapshot=deepcopy(metadata_snapshot if metadata_snapshot is not None else asset.metadata),
                    reference_id_snapshot=reference_id_snapshot if reference_id_snapshot is not None else asset.reference_id,
                    source_version=source_version,
                    restored_from_version=restored_from_version,
                )
            )
            asset.current_version = new_version
            asset.updated_at = _now_iso()
        return asset
