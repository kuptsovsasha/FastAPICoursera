from functools import lru_cache
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = ConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(Settings):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False
    SECRET_KEY: Optional[str] = None
    LOGTAIL_API_KEY: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class TestConfig(GlobalConfig):
    model_config = ConfigDict(env_prefix="TEST_", extra="ignore")


class DevConfig(GlobalConfig):
    model_config = ConfigDict(env_prefix="DEV_", extra="ignore")


class ProdConfig(GlobalConfig):
    model_config = ConfigDict(env_prefix="PROD_", extra="ignore")


@lru_cache()
def get_config() -> GlobalConfig:
    configs = {
        "dev": DevConfig(),
        "test": TestConfig(),
        "prod": ProdConfig(),
    }
    return configs.get(Settings().ENV_STATE, DevConfig())
