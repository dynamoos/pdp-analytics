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
    auth_email: str = Field(..., alias="GOOGLE_AUTH_EMAIL")
    auth_password: str = Field(..., alias="GOOGLE_AUTH_PASSWORD")
    api_key: str = Field(..., alias="GOOGLE_API_KEY")

    model_config = ConfigDict(env_file=".env", populate_by_name=True, extra="ignore")

    @field_validator("credentials_path")
    def validate_credentials_path(cls, v):
        if v and not Path(v).exists():
            # Solo advertir, no fallar si el archivo no existe en tests
            print(f"Warning: Credentials file not found: {v}")
        return v


class MibotSettings(BaseSettings):
    """Mibot API settings"""

    api_base_url: str = Field("https://app.mibot.cl", alias="MIBOT_API_BASE_URL")
    project_uid: str = Field(..., alias="MIBOT_PROJECT_UID")
    client_uid: str = Field(..., alias="MIBOT_CLIENT_UID")

    model_config = ConfigDict(env_file=".env", populate_by_name=True, extra="ignore")


class APISettings(BaseSettings):
    """API configuration"""

    host: str = Field("0.0.0.0", alias="API_HOST")
    port: int = Field(8000, alias="API_PORT")
    prefix: str = Field("/api/v1", alias="API_PREFIX")
    timeout: int = Field(30, alias="API_TIMEOUT_SECONDS")
    max_retries: int = Field(3, alias="API_MAX_RETRIES")
    max_concurrent_calls: int = Field(10, alias="MAX_CONCURRENT_API_CALLS")

    model_config = ConfigDict(env_file=".env", populate_by_name=True, extra="ignore")


class ExcelSettings(BaseSettings):
    """Excel generation settings"""

    output_path: str = Field("./output", alias="EXCEL_OUTPUT_PATH")
    template_path: str = Field("./templates", alias="EXCEL_TEMPLATE_PATH")

    model_config = ConfigDict(env_file=".env", populate_by_name=True, extra="ignore")

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
    _mibot: Optional[MibotSettings] = None
    _api: Optional[APISettings] = None
    _excel: Optional[ExcelSettings] = None

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",  # Esto es clave - ignora campos extras
    )

    @property
    def google(self) -> GoogleSettings:
        if self._google is None:
            self._google = GoogleSettings()
        return self._google

    @property
    def mibot(self) -> MibotSettings:
        if self._mibot is None:
            self._mibot = MibotSettings()
        return self._mibot

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


# Global settings instance
settings = AppSettings()
