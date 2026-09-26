import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import ASSISTANT_AUTHORITY_RULE, ASSISTANT_NAME, ASSISTANT_STYLE
from .models import (
    AssistantIdentity,
    CharacterCreate,
    IdentityUpdate,
    ImageEditRequest,
    MerchDesignCreate,
    NonLinearThoughtRequest,
    PreferenceUpdate,
    StoryCreate,
    UniverseCreate,
)
from .services import KarmaService
from .storage import InMemoryStore


def _get_bool_env(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _get_list_env(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


APP_ENV = os.getenv("APP_ENV", "development")
APP_NAME = os.getenv("APP_NAME", "fastapi-on-azure-functions")
AUTH_ENABLED = _get_bool_env("AUTH_ENABLED", False)
AUTH_BEARER_TOKEN = os.getenv("AUTH_BEARER_TOKEN", "")

ALLOWED_ORIGINS = _get_list_env("CORS_ALLOW_ORIGINS", "*")
ALLOW_CREDENTIALS = _get_bool_env("CORS_ALLOW_CREDENTIALS", False)
ALLOWED_METHODS = _get_list_env("CORS_ALLOW_METHODS", "*")
ALLOWED_HEADERS = _get_list_env("CORS_ALLOW_HEADERS", "*")

app = FastAPI(title=APP_NAME)
bearer_scheme = HTTPBearer(auto_error=False)

store = InMemoryStore()
service = KarmaService(
    store=store,
    identity=AssistantIdentity(
        name=ASSISTANT_NAME,
        tone=ASSISTANT_STYLE,
        authority_rule=ASSISTANT_AUTHORITY_RULE,
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)


async def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    if not AUTH_ENABLED:
        return
    if not AUTH_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTH_BEARER_TOKEN is required when AUTH_ENABLED is true.",
        )
    if credentials is None or credentials.credentials != AUTH_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token.",
        )


@app.get("/sample", dependencies=[Depends(require_auth)])
async def index():
    return {"info": "Try /hello/Shivani for parameterized route.", "environment": APP_ENV}


@app.get("/hello/{name}", dependencies=[Depends(require_auth)])
async def get_name(name: str):
    return {"name": name}


@app.get("/identity", dependencies=[Depends(require_auth)])
async def get_identity():
    return service.identity


@app.put("/identity", dependencies=[Depends(require_auth)])
async def update_identity(payload: IdentityUpdate):
    return service.set_identity(name=payload.name, tone=payload.tone, lore=payload.lore)


@app.get("/preferences", dependencies=[Depends(require_auth)])
async def get_preferences():
    with store.lock:
        return store.preferences


@app.put("/preferences", dependencies=[Depends(require_auth)])
async def update_preferences(payload: PreferenceUpdate):
    return service.update_preferences(payload)


@app.post("/structure-thought", dependencies=[Depends(require_auth)])
async def structure_thought(payload: NonLinearThoughtRequest):
    return service.structure_non_linear_input(payload)


@app.post("/universes", dependencies=[Depends(require_auth)])
async def create_universe(payload: UniverseCreate):
    return service.create_universe(payload)


@app.get("/universes", dependencies=[Depends(require_auth)])
async def list_universes():
    with store.lock:
        return list(store.universes.values())


@app.get("/universes/{universe_id}", dependencies=[Depends(require_auth)])
async def get_universe(universe_id: str):
    with store.lock:
        universe = store.universes.get(universe_id)
    if not universe:
        raise HTTPException(status_code=404, detail="Universe not found.")
    return universe


@app.post("/characters", dependencies=[Depends(require_auth)])
async def create_character(payload: CharacterCreate):
    return service.create_character(payload)


@app.get("/characters", dependencies=[Depends(require_auth)])
async def list_characters(universe_id: str | None = None):
    with store.lock:
        values = list(store.characters.values())
    if not universe_id:
        return values
    return [item for item in values if item.universe_id == universe_id]


@app.post("/stories", dependencies=[Depends(require_auth)])
async def create_story(payload: StoryCreate):
    return service.create_story(payload)


@app.get("/stories", dependencies=[Depends(require_auth)])
async def list_stories(universe_id: str | None = None):
    with store.lock:
        values = list(store.stories.values())
    if not universe_id:
        return values
    return [item for item in values if item.universe_id == universe_id]


@app.post("/merch-designs", dependencies=[Depends(require_auth)])
async def create_merch_design(payload: MerchDesignCreate):
    return service.create_merch_design(payload)


@app.post("/image-edits", dependencies=[Depends(require_auth)])
async def edit_image(payload: ImageEditRequest):
    return service.edit_image(payload)


@app.get("/assets", dependencies=[Depends(require_auth)])
async def list_assets(universe_id: str | None = None):
    with store.lock:
        values = list(store.assets.values())
    if not universe_id:
        return values
    return [item for item in values if item.universe_id == universe_id]


@app.get("/assets/{asset_id}", dependencies=[Depends(require_auth)])
async def get_asset(asset_id: str):
    with store.lock:
        asset = store.assets.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found.")
    return asset


@app.post("/assets/{asset_id}/versions/{version}/restore", dependencies=[Depends(require_auth)])
async def restore_asset(asset_id: str, version: int):
    return service.restore_asset_version(asset_id, version)
