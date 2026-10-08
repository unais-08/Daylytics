from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANALYTICS_", env_file=".env")

    app_name: str = "Personal Analytics API"
    database_url: str = "sqlite:///./analytics.db"
    timezone: str = "Asia/Kolkata"
    deep_work_min_minutes: int = 25
    daily_deep_target_min: int = 240
    daily_distraction_cap_min: int = 120
    daily_career_target_units: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
