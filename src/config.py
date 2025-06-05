from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class UvicornConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="UVICORN_")

    host: str = Field("127.0.0.1")
    port: int = Field(8000)
    workers: int | None = Field(None)
    log_level: str = Field("info")
    reload: bool = Field(False)


class DataBaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str
    port: int = Field(5432)
    user: str
    password: str
    name: str
    debug: bool = Field(False)

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class PrometheusConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="PR_")

    monitor: bool = Field(False)


class AuthConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    secret: str
    alg: str = Field("HS256")
    ttl: int = Field(360)


class ParserConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="PARSER_")

    enabled: bool = Field(False)
    celery_broker_url: str
    celery_backend_url: str
    parser_url: str


class Config(ConfigBase):
    uvicorn: UvicornConfig = Field(default_factory=UvicornConfig)
    db: DataBaseConfig = Field(default_factory=DataBaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    prometheus: PrometheusConfig = Field(default_factory=PrometheusConfig)
    parser: ParserConfig = Field(default_factory=ParserConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()


cfg = Config.load()
