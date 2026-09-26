from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock

from .models import Asset, AssetVersion, Character, Story, Universe, UserPreferenceProfile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryStore:
    def __init__(self) -> None:
        self.lock = RLock()
        self.universes: dict[str, Universe] = {}
        self.characters: dict[str, Character] = {}
        self.stories: dict[str, Story] = {}
        self.assets: dict[str, Asset] = {}
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
                    restored_from_version=restored_from_version,
                )
            )
            asset.current_version = new_version
            asset.updated_at = _now_iso()
        return asset

    def restore_asset_version(self, asset_id: str, version: int) -> Asset:
        with self.lock:
            asset = self.assets[asset_id]
            selected_version = next(item for item in asset.versions if item.version == version)
            asset.metadata = deepcopy(selected_version.metadata_snapshot)
            asset.reference_id = selected_version.reference_id_snapshot
            return self.append_asset_version(
                asset_id,
                summary=f"Restored to version {version}",
                metadata_snapshot=asset.metadata,
                reference_id_snapshot=asset.reference_id,
                restored_from_version=version,
            )
