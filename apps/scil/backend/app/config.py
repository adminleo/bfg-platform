"""SCIL-specific settings extending the shared CoreSettings."""

from bfg_core.config import CoreSettings


class SCILSettings(CoreSettings):
    app_name: str = "SCIL Profile"
    database_url: str = "postgresql+asyncpg://bfg:bfg_dev_2024@db:5432/bfg"


settings = SCILSettings()
