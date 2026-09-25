import fastapi

from .config import ASSISTANT_AUTHORITY_RULE, ASSISTANT_NAME, ASSISTANT_STYLE
from .models import (
    AssistantIdentity,
    CharacterCreate,
    ImageEditRequest,
    MerchDesignCreate,
    NonLinearThoughtRequest,
    PreferenceUpdate,
    StoryCreate,
    UniverseCreate,
)
from .services import KarmaService
from .storage import InMemoryStore

app = fastapi.FastAPI()
store = InMemoryStore()
service = KarmaService(
    store=store,
    identity=AssistantIdentity(
        name=ASSISTANT_NAME,
        tone=ASSISTANT_STYLE,
        authority_rule=ASSISTANT_AUTHORITY_RULE,
    ),
)


@app.get("/sample")
async def index():
    return {
        "info": "Try /hello/Shivani for parameterized route.",
    }


@app.get("/hello/{name}")
async def get_name(name: str):
    return {
        "name": name,
    }


@app.get("/identity")
async def get_identity():
    return service.identity


@app.put("/identity")
async def update_identity(name: str | None = None, tone: str | None = None, lore: str | None = None):
    return service.set_identity(name=name, tone=tone, lore=lore)


@app.get("/preferences")
async def get_preferences():
    return store.preferences


@app.put("/preferences")
async def update_preferences(payload: PreferenceUpdate):
    return service.update_preferences(payload)


@app.post("/structure-thought")
async def structure_thought(payload: NonLinearThoughtRequest):
    return service.structure_non_linear_input(payload)


@app.post("/universes")
async def create_universe(payload: UniverseCreate):
    return service.create_universe(payload)


@app.get("/universes")
async def list_universes():
    return list(store.universes.values())


@app.get("/universes/{universe_id}")
async def get_universe(universe_id: str):
    universe = store.universes.get(universe_id)
    if not universe:
        raise fastapi.HTTPException(status_code=404, detail="Universe not found.")
    return universe


@app.post("/characters")
async def create_character(payload: CharacterCreate):
    return service.create_character(payload)


@app.get("/characters")
async def list_characters(universe_id: str | None = None):
    values = list(store.characters.values())
    if not universe_id:
        return values
    return [item for item in values if item.universe_id == universe_id]


@app.post("/stories")
async def create_story(payload: StoryCreate):
    return service.create_story(payload)


@app.get("/stories")
async def list_stories(universe_id: str | None = None):
    values = list(store.stories.values())
    if not universe_id:
        return values
    return [item for item in values if item.universe_id == universe_id]


@app.post("/merch-designs")
async def create_merch_design(payload: MerchDesignCreate):
    return service.create_merch_design(payload)


@app.post("/image-edits")
async def edit_image(payload: ImageEditRequest):
    return service.edit_image(payload)


@app.get("/assets")
async def list_assets(universe_id: str | None = None):
    values = list(store.assets.values())
    if not universe_id:
        return values
    return [item for item in values if item.universe_id == universe_id]


@app.get("/assets/{asset_id}")
async def get_asset(asset_id: str):
    asset = store.assets.get(asset_id)
    if not asset:
        raise fastapi.HTTPException(status_code=404, detail="Asset not found.")
    return asset


@app.post("/assets/{asset_id}/versions/{version}/restore")
async def restore_asset(asset_id: str, version: int):
    return service.restore_asset_version(asset_id, version)
