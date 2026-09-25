import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


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
