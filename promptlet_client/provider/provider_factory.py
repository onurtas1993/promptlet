from promptlet_client.provider.anthropic_provider import AnthropicProvider
from promptlet_client.provider.base_provider import BaseProvider
from promptlet_client.provider.openai_provider import OpenAIProvider


class ProviderFactory:
    @staticmethod
    def create(provider_name: str) -> BaseProvider:
        normalized_name = provider_name.strip().lower()

        if normalized_name == "anthropic":
            return AnthropicProvider()

        if normalized_name == "openai":
            return OpenAIProvider()

        raise ValueError(
            f"Unsupported provider '{provider_name}'. Use 'anthropic' or 'openai'."
        )
