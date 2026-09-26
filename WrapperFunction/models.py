from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AssistantIdentity(BaseModel):
    name: str = "Karma"
    tone: str
    lore: str = ""
    authority_rule: str = "User is the final decision-maker; assistant advises and executes."


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
    traits: List[str] = Field(default_factory=list)


class Character(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("char"))
    universe_id: str
    name: str
    backstory: str = ""
    lore_notes: str = ""
    traits: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)


class StoryCreate(BaseModel):
    universe_id: str
    title: str
    arc: str
    backstory: str = ""
    lore: str = ""
    character_ids: List[str] = Field(default_factory=list)
    crossover_universe_ids: List[str] = Field(default_factory=list)
    allow_crossover: bool = False


class Story(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("story"))
    universe_id: str
    title: str
    arc: str
    backstory: str = ""
    lore: str = ""
    character_ids: List[str] = Field(default_factory=list)
    crossover_universe_ids: List[str] = Field(default_factory=list)
    continuity_notes: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)


class MerchDesignCreate(BaseModel):
    universe_id: str
    product_type: Literal["hoodie", "tshirt"]
    theme_prompt: str
    print_area: Literal["front", "back", "sleeve", "full"]
    variants: List[str] = Field(default_factory=list)
    export_formats: List[str] = Field(default_factory=lambda: ["png"])


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
    created_at: str = Field(default_factory=_now_iso)


class Asset(BaseModel):
    id: str = Field(default_factory=lambda: _new_id("asset"))
    universe_id: str
    asset_type: Literal["story", "character", "merch_design", "image_edit"]
    reference_id: str
    metadata: dict = Field(default_factory=dict)
    versions: List[AssetVersion] = Field(default_factory=list)
    current_version: int = 0
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


class ModerationResult(BaseModel):
    allowed: bool
    reason: Optional[str] = None


class UserPreferenceProfile(BaseModel):
    likes: List[str] = Field(default_factory=list)
    dislikes: List[str] = Field(default_factory=list)
    output_preferences: List[str] = Field(default_factory=list)
    thinking_profile: str = "non-linear"
    desired_assistant_behavior: str = "Straight feedback when ideas are not feasible; user is always the final authority."
    updated_at: str = Field(default_factory=_now_iso)


class PreferenceUpdate(BaseModel):
    likes: List[str] = Field(default_factory=list)
    dislikes: List[str] = Field(default_factory=list)
    output_preferences: List[str] = Field(default_factory=list)
    thinking_profile: str = "non-linear"
    desired_assistant_behavior: str = "Straight feedback when ideas are not feasible; user is always the final authority."


class NonLinearThoughtRequest(BaseModel):
    raw_input: str
    goal: str = ""
    constraints: List[str] = Field(default_factory=list)


class StructuredThoughtResponse(BaseModel):
    summary: str
    assumptions: List[str] = Field(default_factory=list)
    phases: List[str] = Field(default_factory=list)
    feasibility: Literal["works", "won't_work_without_changes"]
    straight_feedback: str
