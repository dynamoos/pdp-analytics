from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field, validator


class GoogleSettings(BaseSettings):
    """Google Cloud and Auth settings"""

    project_id: str = Field(..., env="GCP_PROJECT_ID")
    credentials_path: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    auth_email: str = Field(..., env="GOOGLE_AUTH_EMAIL")
    auth_password: str = Field(..., env="GOOGLE_AUTH_PASSWORD")
    api_key: str = Field(..., env="GOOGLE_API_KEY")

    @validator("credentials_path")
    def validate_credentials_path(cls, v):
        if v and not Path(v).exists():
            raise ValueError(f"Credentials file not found: {v}")
        return v


class MibotSettings(BaseSettings):
    """Mibot API settings"""

    api_base_url: str = Field("https://app.mibot.cl", env="MIBOT_API_BASE_URL")
    project_uid: str = Field(..., env="MIBOT_PROJECT_UID")
    client_uid: str = Field(..., env="MIBOT_CLIENT_UID")


class APISettings(BaseSettings):
    """API configuration"""

    host: str = Field("0.0.0.0", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    prefix: str = Field("/api/v1", env="API_PREFIX")
    timeout: int = Field(30, env="API_TIMEOUT_SECONDS")
    max_retries: int = Field(3, env="API_MAX_RETRIES")
    max_concurrent_calls: int = Field(10, env="MAX_CONCURRENT_API_CALLS")


class ExcelSettings(BaseSettings):
    """Excel generation settings"""

    output_path: str = Field("./output", env="EXCEL_OUTPUT_PATH")
    template_path: str = Field("./templates", env="EXCEL_TEMPLATE_PATH")

    @validator("output_path", "template_path")
    def create_directory(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)


class AppSettings(BaseSettings):
    """Application settings"""

    env: str = Field("development", env="APP_ENV")
    name: str = Field("Telefonica PDP Analytics", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # Sub-configurations
    google: GoogleSettings = GoogleSettings()
    mibot: MibotSettings = MibotSettings()
    api: APISettings = APISettings()
    excel: ExcelSettings = ExcelSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = AppSettings()
