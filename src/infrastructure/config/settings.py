from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class GoogleSettings(BaseSettings):
    """Google Cloud and Auth settings"""

    project_id: str = Field(..., alias="GCP_PROJECT_ID")
    credentials_path: Optional[str] = Field(
        None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    auth_email: str = Field(..., alias="GOOGLE_AUTH_EMAIL")
    auth_password: str = Field(..., alias="GOOGLE_AUTH_PASSWORD")
    api_key: str = Field(..., alias="GOOGLE_API_KEY")

    @field_validator("credentials_path")
    def validate_credentials_path(cls, v):
        if v and not Path(v).exists():
            raise ValueError(f"Credentials file not found: {v}")
        return v

    class Config:
        env_file = ".env"
        populate_by_name = True


class MibotSettings(BaseSettings):
    """Mibot API settings"""

    api_base_url: str = Field("https://app.mibot.cl", alias="MIBOT_API_BASE_URL")
    project_uid: str = Field(..., alias="MIBOT_PROJECT_UID")
    client_uid: str = Field(..., alias="MIBOT_CLIENT_UID")

    class Config:
        env_file = ".env"
        populate_by_name = True


class APISettings(BaseSettings):
    """API configuration"""

    host: str = Field("0.0.0.0", alias="API_HOST")
    port: int = Field(8000, alias="API_PORT")
    prefix: str = Field("/api/v1", alias="API_PREFIX")
    timeout: int = Field(30, alias="API_TIMEOUT_SECONDS")
    max_retries: int = Field(3, alias="API_MAX_RETRIES")
    max_concurrent_calls: int = Field(10, alias="MAX_CONCURRENT_API_CALLS")

    class Config:
        env_file = ".env"
        populate_by_name = True


class ExcelSettings(BaseSettings):
    """Excel generation settings"""

    output_path: str = Field("./output", alias="EXCEL_OUTPUT_PATH")
    template_path: str = Field("./templates", alias="EXCEL_TEMPLATE_PATH")

    @field_validator("output_path", "template_path")
    def create_directory(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    class Config:
        env_file = ".env"
        populate_by_name = True


class AppSettings(BaseSettings):
    """Application settings"""

    env: str = Field("development", alias="APP_ENV")
    name: str = Field("Telefonica PDP Analytics", alias="APP_NAME")
    debug: bool = Field(True, alias="DEBUG")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    @property
    def google(self) -> GoogleSettings:
        return GoogleSettings()

    @property
    def mibot(self) -> MibotSettings:
        return MibotSettings()

    @property
    def api(self) -> APISettings:
        return APISettings()

    @property
    def excel(self) -> ExcelSettings:
        return ExcelSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True


# Global settings instance - no se inicializa hasta que se importe
settings = AppSettings()
