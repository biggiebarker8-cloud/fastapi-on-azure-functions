from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Dict

from .knowledge_base import load_default_knowledge_bases
from .models import Asset, AssetVersion, Character, KnowledgeBaseEntry, Story, Universe, UserPreferenceProfile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryStore:
    def __init__(self) -> None:
        self.lock = RLock()
        self.universes: Dict[str, Universe] = {}
        self.characters: Dict[str, Character] = {}
        self.stories: Dict[str, Story] = {}
        self.assets: Dict[str, Asset] = {}
        self.knowledge_bases: Dict[str, KnowledgeBaseEntry] = load_default_knowledge_bases()
        self.preferences: UserPreferenceProfile = UserPreferenceProfile()

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

    def append_asset_version(
        self,
        asset_id: str,
        summary: str,
        metadata_snapshot: dict | None = None,
        reference_id_snapshot: str | None = None,
        source_version: int | None = None,
    ) -> Asset:
        with self.lock:
            asset = self.assets[asset_id]
            new_version = asset.current_version + 1
            asset.versions.append(
                AssetVersion(
                    version=new_version,
                    content_summary=summary,
                    metadata_snapshot=metadata_snapshot if metadata_snapshot is not None else dict(asset.metadata),
                    reference_id_snapshot=reference_id_snapshot if reference_id_snapshot is not None else asset.reference_id,
                    source_version=source_version,
                )
            )
            asset.current_version = new_version
            asset.updated_at = _now_iso()
        return asset
