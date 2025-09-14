"""
Configuration management module for MentorBot.

This module defines all configuration classes and settings for the Telegram bot,
including database connections, Redis configuration, payment provider settings,
and common bot parameters. All settings are loaded from environment variables
with proper validation using Pydantic.
"""

import json
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL


class BaseSettings(_BaseSettings):
    """
    Base settings class with common configuration for all environment-based settings.
    
    Provides automatic loading from .env file with UTF-8 encoding and ignores
    extra fields not defined in the model.
    """
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class CommonConfig(BaseSettings, env_prefix="COMMON_"):
    """
    Common bot configuration settings.
    
    Contains essential bot parameters like token, admin list, and encryption settings.
    All settings are prefixed with 'COMMON_' in environment variables.
    """
    bot_token: SecretStr  # Telegram bot token for API access
    admins: list[int]  # List of admin user IDs who can access admin functions
    encryption_key: SecretStr  # Key for encrypting sensitive user data
    encryption_on: bool = True  # Whether to enable data encryption


class PostgresConfig(BaseSettings, env_prefix="POSTGRES_"):
    """
    PostgreSQL database configuration.
    
    Manages database connection parameters and provides DSN building functionality.
    All settings are prefixed with 'POSTGRES_' in environment variables.
    """
    host: str  # Database host address
    port: int  # Database port number
    user: str  # Database username
    password: SecretStr  # Database password
    db: str  # Database name

    enable_logging: bool = False  # Whether to enable SQLAlchemy query logging

    def build_dsn(self) -> str:
        """
        Build PostgreSQL connection DSN string.
        
        Returns:
            str: Complete database connection string for asyncpg driver
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db,
        ).render_as_string(hide_password=False)


class RedisConfig(BaseSettings, env_prefix="REDIS_"):
    """
    Redis configuration for caching and session storage.
    
    Manages Redis connection parameters for FSM storage and caching.
    All settings are prefixed with 'REDIS_' in environment variables.
    """
    use_redis: bool = True  # Whether to use Redis for FSM storage (fallback to memory if False)
    host: str  # Redis server host address
    port: int  # Redis server port number
    password: str  # Redis server password


class ProviderConfig(BaseSettings, env_prefix="PROVIDER_"):
    """
    Payment provider configuration for subscription and mentor purchases.
    
    Manages payment processing settings including prices, currency, and receipt generation.
    All settings are prefixed with 'PROVIDER_' in environment variables.
    """
    token: str  # Payment provider API token
    currency: str  # Currency code (e.g., 'RUB', 'USD')
    price: int  # Subscription price in smallest currency unit (kopecks/cents)
    mentor_price: int  # Individual mentor purchase price in smallest currency unit
    enabled: bool = True  # Whether payment system is enabled

    def provider_data(self, price: int, description: str) -> str:
        """
        Generate payment provider receipt data in JSON format.
        
        Args:
            price: Price in smallest currency unit (kopecks/cents)
            description: Product description for the receipt
            
        Returns:
            str: JSON-formatted receipt data for payment provider
        """
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
    """
    Main configuration container for the entire application.
    
    Combines all configuration sections into a single, validated configuration object
    that can be easily passed throughout the application.
    """
    common: CommonConfig  # Common bot settings
    redis: RedisConfig  # Redis configuration
    postgres: PostgresConfig  # PostgreSQL database configuration
    provider_config: ProviderConfig  # Payment provider configuration


def create_config() -> Config:
    """
    Create and return a complete configuration object.
    
    Initializes all configuration sections from environment variables and returns
    a validated Config object ready for use throughout the application.
    
    Returns:
        Config: Complete configuration object with all settings loaded and validated
    """
    return Config(
        common=CommonConfig(),
        redis=RedisConfig(),
        postgres=PostgresConfig(),
        provider_config=ProviderConfig(),
    )
