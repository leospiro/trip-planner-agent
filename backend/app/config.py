from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    llm_model_id: str = os.getenv("LLM_MODEL_ID", "")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_timeout: int = int(os.getenv("LLM_TIMEOUT", "120"))
    
    amap_api_key: str = os.getenv("AMAP_API_KEY", "")
    unsplash_access_key: str = os.getenv("UNSPLASH_ACCESS_KEY", "")
    
    # 小红书集成配置
    xhs_rsshub_base_url: str = os.getenv("XHS_RSSHUB_BASE_URL", "http://localhost:1200")
    xhs_rsshub_fallback_url: str = os.getenv("XHS_RSSHUB_FALLBACK_URL", "https://rsshub.pseudoyu.com")
    xhs_cookie: Optional[str] = os.getenv("XHS_COOKIE", None)

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

def get_settings():
    return Settings()

def get_effective_keys(api_keys=None):
    """获取有效的 API Keys，用户提供的优先于 .env 配置"""
    settings = get_settings()
    return {
        "llm_api_key": (api_keys.llm_api_key if api_keys and api_keys.llm_api_key else settings.llm_api_key),
        "llm_model_id": (api_keys.llm_model_id if api_keys and api_keys.llm_model_id else settings.llm_model_id),
        "llm_base_url": (api_keys.llm_base_url if api_keys and api_keys.llm_base_url else settings.llm_base_url),
        "amap_api_key": (api_keys.amap_api_key if api_keys and api_keys.amap_api_key else settings.amap_api_key),
        "unsplash_access_key": (api_keys.unsplash_access_key if api_keys and api_keys.unsplash_access_key else settings.unsplash_access_key),
    }
