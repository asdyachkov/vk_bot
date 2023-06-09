import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str
    salt: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class DatabaseConfig:
    url: str = "postgresql+asyncpg://pwaehjqg:x5lVnQaSiJNr8bMbSTJaTbIwWEQtkOek@ruby.db.elephantsql.com/pwaehjqg"
    host: str = "localhost"
    port: int = 5432
    user: str = "ruby.db.elephantsql.com"
    password: str = "x5lVnQaSiJNr8bMbSTJaTbIwWEQtkOek"
    database: str = "pwaehjqg"


@dataclass
class Config:
    admin: AdminConfig = None
    session: SessionConfig = None
    bot: BotConfig = None
    database: DatabaseConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        admin=AdminConfig(
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
            salt=raw_config["admin"]["salt"],
        ),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
            group_id=raw_config["bot"]["group_id"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
    )
