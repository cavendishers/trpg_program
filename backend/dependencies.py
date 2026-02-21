"""Dependency injection - service singletons for FastAPI."""

from backend.ai.providers.base import AIProviderBase, create_provider
from backend.character.service import CharacterService
from backend.config import settings
from backend.scenario.loader import ScenarioLoader


_character_service: CharacterService | None = None
_scenario_loader: ScenarioLoader | None = None
_ai_provider: AIProviderBase | None = None


def get_character_service() -> CharacterService:
    global _character_service
    if _character_service is None:
        _character_service = CharacterService()
    return _character_service


def get_scenario_loader() -> ScenarioLoader:
    global _scenario_loader
    if _scenario_loader is None:
        _scenario_loader = ScenarioLoader(settings.scenarios_dir)
    return _scenario_loader


def get_ai_provider() -> AIProviderBase:
    global _ai_provider
    if _ai_provider is None:
        provider_name = settings.ai_provider
        if provider_name == "claude":
            _ai_provider = create_provider(
                "claude",
                api_key=settings.anthropic_api_key,
                model=settings.ai_model,
            )
        elif provider_name == "openai":
            _ai_provider = create_provider(
                "openai",
                api_key=settings.openai_api_key,
                model=settings.ai_model,
                base_url=settings.openai_base_url,
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    return _ai_provider
