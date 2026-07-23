"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class ConfigurationError(ValueError):
    """Raised when an application setting is missing or invalid."""


def _required_environment_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise ConfigurationError(
            f"The required environment variable {name!r} is not configured."
        )

    return value


def _database_port() -> int:
    raw_port = _required_environment_variable("DB_PORT")

    try:
        port = int(raw_port)
    except ValueError as error:
        raise ConfigurationError("DB_PORT must be a valid integer.") from error

    if not 1 <= port <= 65535:
        raise ConfigurationError("DB_PORT must be between 1 and 65535.")

    return port


@dataclass(frozen=True, slots=True)
class Settings:
    """Settings required to connect EduMove to its database."""

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_charset: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and validate the application settings once per process."""

    load_dotenv(ENV_FILE)

    return Settings(
        db_host=_required_environment_variable("DB_HOST").strip(),
        db_port=_database_port(),
        db_name=_required_environment_variable("DB_NAME").strip(),
        db_user=_required_environment_variable("DB_USER").strip(),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_charset=_required_environment_variable("DB_CHARSET").strip(),
    )
