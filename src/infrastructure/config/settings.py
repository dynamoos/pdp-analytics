from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class GoogleSettings(BaseSettings):
    """Google Cloud and Auth settings"""

    project_id: str = Field(..., alias="GCP_PROJECT_ID")
    credentials_path: Optional[str] = Field(
        None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    location: str = Field(
        "us-east1",
        alias="GCP_BIGQUERY_LOCATION",
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_validator("credentials_path")
    def validate_credentials_path(cls, v):
        if v and not Path(v).exists():
            print(f"Warning: Credentials file not found: {v}")
        return v


class PostgresSettings(BaseSettings):
    """PostgreSQL configuration with validation"""

    host: str = Field(..., alias="POSTGRES_HOST")
    port: int = Field(5432, alias="POSTGRES_PORT")
    database: str = Field(..., alias="POSTGRES_DB")
    user: str = Field(..., alias="POSTGRES_USER")
    password: str = Field(..., alias="POSTGRES_PASSWORD")

    min_pool_size: int = Field(5, alias="POSTGRES_MIN_POOL_SIZE")
    max_pool_size: int = Field(20, alias="POSTGRES_MAX_POOL_SIZE")
    ssl_mode: str = Field("prefer", alias="POSTGRES_SSL_MODE")

    @property
    def connection_string(self) -> str:
        base = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        params = []
        if self.ssl_mode != "disable":
            params.append(f"sslmode={self.ssl_mode}")
        if params:
            return f"{base}?{'&'.join(params)}"
        return base

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class APISettings(BaseSettings):
    """API configuration"""

    host: str = Field("0.0.0.0", alias="API_HOST")
    port: int = Field(8000, alias="API_PORT")
    prefix: str = Field("/api/v1", alias="API_PREFIX")
    timeout: int = Field(30, alias="API_TIMEOUT_SECONDS")
    max_retries: int = Field(3, alias="API_MAX_RETRIES")
    max_concurrent_calls: int = Field(10, alias="MAX_CONCURRENT_API_CALLS")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class ExcelSettings(BaseSettings):
    """Excel generation settings"""

    output_path: str = Field("./output", alias="EXCEL_OUTPUT_PATH")
    template_path: str = Field("./templates", alias="EXCEL_TEMPLATE_PATH")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @field_validator("output_path", "template_path")
    def create_directory(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)


class AppSettings(BaseSettings):
    """Application settings"""

    env: str = Field("development", alias="APP_ENV")
    name: str = Field("Telefonica PDP Analytics", alias="APP_NAME")
    debug: bool = Field(True, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    # Cached instances
    _google: Optional[GoogleSettings] = None
    _postgres: Optional[PostgresSettings] = None
    _api: Optional[APISettings] = None
    _excel: Optional[ExcelSettings] = None

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def google(self) -> GoogleSettings:
        if self._google is None:
            self._google = GoogleSettings()
        return self._google

    @property
    def postgres(self) -> PostgresSettings:
        if self._postgres is None:
            self._postgres = PostgresSettings()
        return self._postgres

    @property
    def api(self) -> APISettings:
        if self._api is None:
            self._api = APISettings()
        return self._api

    @property
    def excel(self) -> ExcelSettings:
        if self._excel is None:
            self._excel = ExcelSettings()
        return self._excel

    def to_container_config(self) -> dict:
        """Convert all settings to container config format"""

        postgres_config = self.postgres.model_dump()
        postgres_config["connection_string"] = self.postgres.connection_string

        return {
            "google": self.google.model_dump(),
            "postgres": postgres_config,
            "api": self.api.model_dump(),
            "excel": self.excel.model_dump(),
            "app": {
                "env": self.env,
                "name": self.name,
                "debug": self.debug,
                "log_level": self.log_level,
            },
        }


# Global settings instance
settings = AppSettings()
