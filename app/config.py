from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    alpaca_api_key: str = Field(alias="ALPACA_API_KEY")
    alpaca_secret_key: str = Field(alias="ALPACA_SECRET_KEY")
    alpaca_base_url: str = Field(alias="ALPACA_BASE_URL", default="https://paper-api.alpaca.markets")
    alpaca_data_url: str = Field(alias="ALPACA_DATA_URL", default="https://data.alpaca.markets")
    env: str = Field(alias="ENV", default="development")
    db_url: str = Field(alias="DB_URL", default="sqlite:///./trading.db")
    port: int = Field(alias="PORT", default=8000)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
