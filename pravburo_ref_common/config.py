from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str
    referral_db_schema: str = Field(
        default="referral",
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )


@lru_cache
def get_common_settings() -> CommonSettings:
    return CommonSettings()  # type: ignore[call-arg]
