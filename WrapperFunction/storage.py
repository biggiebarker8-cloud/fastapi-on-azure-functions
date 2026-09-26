from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from .models import Asset, AssetVersion, Character, Story, Universe, UserPreferenceProfile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryStore:
    def __init__(self) -> None:
        self.universes: Dict[str, Universe] = {}
        self.characters: Dict[str, Character] = {}
        self.stories: Dict[str, Story] = {}
        self.assets: Dict[str, Asset] = {}
        self.preferences: UserPreferenceProfile = UserPreferenceProfile()

    def add_universe(self, universe: Universe) -> Universe:
        self.universes[universe.id] = universe
        return universe

    def add_character(self, character: Character) -> Character:
        self.characters[character.id] = character
        return character

    def add_story(self, story: Story) -> Story:
        self.stories[story.id] = story
        return story

    def add_asset(self, asset: Asset) -> Asset:
        self.assets[asset.id] = asset
        return asset

    def append_asset_version(
        self,
        asset_id: str,
        summary: str,
        metadata_snapshot: dict | None = None,
        source_version: int | None = None,
    ) -> Asset:
        asset = self.assets[asset_id]
        new_version = asset.current_version + 1
        asset.versions.append(
            AssetVersion(
                version=new_version,
                content_summary=summary,
                metadata_snapshot=metadata_snapshot if metadata_snapshot is not None else dict(asset.metadata),
                source_version=source_version,
            )
        )
        asset.current_version = new_version
        asset.updated_at = _now_iso()
        return asset
