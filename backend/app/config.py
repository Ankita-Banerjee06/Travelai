from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the .env file relative to this file's location, not the process's
# current working directory. Without this, running `uvicorn app.main:app`
# from a different folder (e.g. the repo root vs. the `backend` folder)
# silently fails to load .env and every setting falls back to its default
# (e.g. DATABASE_URL becomes "").
#
# This file lives at backend/app/config.py, so the repo layout is:
#   Travelai/.env                <- primary location (checked first)
#   Travelai/backend/.env        <- fallback location
_APP_DIR = Path(__file__).resolve().parent          # .../backend/app
_BACKEND_DIR = _APP_DIR.parent                       # .../backend
_REPO_ROOT = _BACKEND_DIR.parent                     # .../Travelai

_ENV_CANDIDATES = [_REPO_ROOT / ".env", _BACKEND_DIR / ".env"]
_ENV_FILE = next((str(p) for p in _ENV_CANDIDATES if p.exists()), str(_REPO_ROOT / ".env"))


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    GROQ_API_KEY: str = ""
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        extra="ignore",
    )


@lru_cache
def get_settings():
    settings = Settings()
    if not settings.DATABASE_URL:
        raise RuntimeError(
            f"DATABASE_URL is not set. Looked for a .env file at: {_ENV_FILE}\n"
            "Either place a .env file at the repo root (next to /backend and /frontend) "
            "with DATABASE_URL=postgresql://... set, or export DATABASE_URL as an actual "
            "environment variable before starting uvicorn."
        )
    return settings
