from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    ai_provider: str = "claude"
    ai_model: str = "claude-sonnet-4-20250514"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    ollama_base_url: str = "http://localhost:11434"

    scenarios_dir: str = "scenarios"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
