"""运行期配置：全部从环境变量注入（12-Factor），代码里零硬编码路径。"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_path: Path = REPO_ROOT / "ml-text" / "models" / "text_clf.joblib"
    app_name: str = "news-text-classifier"
    version: str = "1.0.0"
    min_text_len: int = 10
    max_text_len: int = 20000
    log_json: bool = True
    api_token: str = ""
    port: int = 8000
    workers: int = 1

    model_config = {"env_prefix": "DEPLOY_"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
