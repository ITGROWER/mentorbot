import json
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseSettings(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class CommonConfig(BaseSettings, env_prefix="COMMON_"):
    bot_token: SecretStr
    admins: list[int]
    encryption_key: SecretStr
    encryption_on: bool = True


class PostgresConfig(BaseSettings, env_prefix="POSTGRES_"):
    host: str
    port: int
    user: str
    password: SecretStr
    db: str

    enable_logging: bool = False

    def build_dsn(self) -> str:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        ).render_as_string(hide_password=False)


class RedisConfig(BaseSettings, env_prefix="REDIS_"):
    use_redis: bool = True

    host: str
    port: int
    password: str


class ProviderConfig(BaseSettings, env_prefix="PROVIDER_"):
    token: str
    currency: str
    price: int  # в копейках или центах
    mentor_price: int  # стоимость ментора
    enabled: bool = True

    def provider_data(self, price: int, description: str) -> str:
        return json.dumps(
            {
                "receipt": {
                    "items": [
                        {
                            "description": description,
                            "quantity": "1.00",
                            "amount": {
                                "value": f"{price / 100:.2f}",
                                "currency": self.currency,
                            },
                            "vat_code": 1,
                        }
                    ]
                }
            }
        )


class Config(BaseModel):
    common: CommonConfig
    redis: RedisConfig
    postgres: PostgresConfig
    provider_config: ProviderConfig


def create_config() -> Config:
    return Config(
        common=CommonConfig(),
        redis=RedisConfig(),
        postgres=PostgresConfig(),
        provider_config=ProviderConfig(),
    )
