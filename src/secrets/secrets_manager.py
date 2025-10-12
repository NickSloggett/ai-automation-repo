"""Secrets manager with multiple provider support."""

import os
from typing import Any, Dict, List, Optional

from ..config import get_settings
from .providers import SecretsProvider, EnvProvider, VaultProvider, AWSSecretsProvider


class SecretsManager:
    """Central secrets management with fallback providers."""

    def __init__(self):
        self.settings = get_settings()
        self.providers: Dict[str, SecretsProvider] = {}
        self.provider_priority: List[str] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize secrets providers."""
        if self._initialized:
            return

        # Environment provider (always available as fallback)
        self.providers["env"] = EnvProvider()

        # Vault provider
        vault_url = os.getenv("VAULT_URL")
        vault_token = os.getenv("VAULT_TOKEN")
        if vault_url and vault_token:
            try:
                self.providers["vault"] = VaultProvider(
                    url=vault_url,
                    token=vault_token
                )
                self.provider_priority.insert(0, "vault")
            except Exception as e:
                print(f"Failed to initialize Vault provider: {e}")

        # AWS Secrets Manager
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"):
            try:
                self.providers["aws"] = AWSSecretsProvider(region_name=aws_region)
                self.provider_priority.insert(0, "aws")
            except Exception as e:
                print(f"Failed to initialize AWS provider: {e}")

        # Add env as lowest priority
        self.provider_priority.append("env")
        self._initialized = True

    async def get_secret(self, key: str, default: Any = None) -> Optional[str]:
        """Get secret from the highest priority provider that has it."""
        await self.initialize()

        for provider_name in self.provider_priority:
            provider = self.providers.get(provider_name)
            if provider:
                try:
                    value = await provider.get_secret(key)
                    if value is not None:
                        return value
                except Exception as e:
                    print(f"Error getting secret from {provider_name}: {e}")
                    continue

        return default

    async def set_secret(self, key: str, value: str, provider: str = "auto") -> None:
        """Set secret in specified provider (or auto-select)."""
        await self.initialize()

        if provider == "auto":
            # Use highest priority provider that supports writing
            for provider_name in self.provider_priority:
                if provider_name != "env":  # Don't write to env in production
                    provider_obj = self.providers.get(provider_name)
                    if provider_obj:
                        try:
                            await provider_obj.set_secret(key, value)
                            return
                        except Exception as e:
                            print(f"Failed to set secret in {provider_name}: {e}")
                            continue

            # Fallback to env
            await self.providers["env"].set_secret(key, value)

        else:
            provider_obj = self.providers.get(provider)
            if not provider_obj:
                raise ValueError(f"Provider {provider} not available")
            await provider_obj.set_secret(key, value)

    async def delete_secret(self, key: str, provider: str = "all") -> None:
        """Delete secret from providers."""
        await self.initialize()

        if provider == "all":
            for provider_obj in self.providers.values():
                try:
                    await provider_obj.delete_secret(key)
                except Exception as e:
                    print(f"Failed to delete secret from provider: {e}")
        else:
            provider_obj = self.providers.get(provider)
            if provider_obj:
                await provider_obj.delete_secret(key)

    async def list_secrets(self, prefix: str = "", provider: str = "auto") -> Dict[str, str]:
        """List secrets with prefix."""
        await self.initialize()

        if provider == "auto":
            # Merge secrets from all providers
            all_secrets = {}
            for provider_obj in self.providers.values():
                try:
                    provider_secrets = await provider_obj.list_secrets(prefix)
                    all_secrets.update(provider_secrets)
                except Exception as e:
                    print(f"Failed to list secrets from provider: {e}")

            return all_secrets
        else:
            provider_obj = self.providers.get(provider)
            if provider_obj:
                return await provider_obj.list_secrets(prefix)
            return {}

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        return {
            "providers": list(self.providers.keys()),
            "priority": self.provider_priority,
            "initialized": self._initialized,
        }


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


async def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
        await _secrets_manager.initialize()
    return _secrets_manager


# Convenience functions for common secrets
async def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from secrets."""
    manager = await get_secrets_manager()
    return await manager.get_secret("OPENAI_API_KEY")


async def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from secrets."""
    manager = await get_secrets_manager()
    return await manager.get_secret("ANTHROPIC_API_KEY")


async def get_database_url() -> Optional[str]:
    """Get database URL from secrets."""
    manager = await get_secrets_manager()
    return await manager.get_secret("DATABASE_URL")
