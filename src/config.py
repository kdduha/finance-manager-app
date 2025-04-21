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


class AuthConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    secret: str
    alg: str = Field("HS256")
    ttl: int = Field(360)


class Config(ConfigBase):
    uvicorn: UvicornConfig = Field(default_factory=UvicornConfig)
    db: DataBaseConfig = Field(default_factory=DataBaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()


cfg = Config.load()
