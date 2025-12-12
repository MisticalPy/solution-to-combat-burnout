from dataclasses import dataclass, field
from environs import Env
from typing import Dict, Any


@dataclass
class TgBot:
    token: str


@dataclass
class LogSettings:
    log_lvl: str
    format: str


@dataclass
class RedisSettings:
    host: str
    port: int
    db: int
    password: str
    username: str


@dataclass
class DatabaseSettings:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class Config:
    bot: TgBot
    log: LogSettings
    redis: RedisSettings
    db: DatabaseSettings


def load_config(path: None | str = None) -> Config:

    env: Env = Env()
    env.read_env(path, override=True)

    redis = RedisSettings(
        host=env("REDIS_HOST"),
        port=env.int("REDIS_PORT"),
        db=env.int("REDIS_DATABASE"),
        password=env("REDIS_PASSWORD", default=""),
        username=env("REDIS_USERNAME", default=""),
    )

    db = DatabaseSettings(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
    )

    return Config(bot=TgBot(token=env("BOT_TOKEN")),
                  log=LogSettings(log_lvl=env("LOG_LEVEL"),
                                  format=env("LOG_FORMAT")),
                  redis=redis,
                  db=db)
