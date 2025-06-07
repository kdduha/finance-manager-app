from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file="./graphql_parser/.env", env_file_encoding="utf-8", extra="ignore")


class UvicornConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="UVICORN_")

    host: str = Field("127.0.0.1")
    port: int = Field(8090)
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


class Config(ConfigBase):
    uvicorn: UvicornConfig = Field(default_factory=UvicornConfig)
    db: DataBaseConfig = Field(default_factory=DataBaseConfig)

    @classmethod
    def load(cls) -> "Config":
        return cls()


cfg = Config.load()
