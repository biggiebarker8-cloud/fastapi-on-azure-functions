from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

from .models import (
    Asset,
    AssistantIdentity,
    Character,
    CharacterCreate,
    ImageEditRequest,
    MerchDesignCreate,
    NonLinearThoughtRequest,
    PreferenceUpdate,
    Story,
    StoryCreate,
    StructuredThoughtResponse,
    Universe,
    UniverseCreate,
    UserPreferenceProfile,
)
from .moderation import moderate_text
from .storage import InMemoryStore


class KarmaService:
    def __init__(self, store: InMemoryStore, identity: AssistantIdentity) -> None:
        self.store = store
        self.identity = identity

    def set_identity(self, name: str | None = None, tone: str | None = None, lore: str | None = None) -> AssistantIdentity:
        with self.store.lock:
            if name:
                self.identity.name = name
            if tone:
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
        with self.store.lock:
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
            story = Story(
                **story_payload,
                continuity_notes=continuity_notes,
            )
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
                f"theme='{payload.theme_prompt}', variants={payload.variants}, exports={payload.export_formats}"
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

            summary = f"{payload.operation}: {payload.instructions}"
            asset = self._add_asset(
                "image_edit",
                reference_id=payload.source_asset_id,
                universe_id=payload.universe_id,
                metadata=payload.model_dump(),
                initial_summary=summary,
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
                source_version=current_version_before_restore,
            )
            asset.metadata = dict(selected_version.metadata_snapshot)
            if selected_version.reference_id_snapshot is not None:
                asset.reference_id = selected_version.reference_id_snapshot
            summary = f"Restored from version {version}"
            self.store.append_asset_version(
                asset_id,
                summary,
                metadata_snapshot=dict(asset.metadata),
                source_version=version,
            )
            return self.store.assets[asset_id]

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
            self.store.append_asset_version(asset.id, initial_summary, metadata_snapshot=dict(metadata))
        return asset
