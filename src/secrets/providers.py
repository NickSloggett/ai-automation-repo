"""Secrets providers for different backends."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import hvac
import boto3
from botocore.exceptions import ClientError


class SecretsProvider(ABC):
    """Base class for secrets providers."""

    @abstractmethod
    async def get_secret(self, key: str, default: Any = None) -> Optional[str]:
        """Get a secret value."""
        pass

    @abstractmethod
    async def set_secret(self, key: str, value: str) -> None:
        """Set a secret value."""
        pass

    @abstractmethod
    async def delete_secret(self, key: str) -> None:
        """Delete a secret."""
        pass

    @abstractmethod
    async def list_secrets(self, prefix: str = "") -> Dict[str, str]:
        """List secrets with optional prefix."""
        pass


class EnvProvider(SecretsProvider):
    """Environment variable secrets provider."""

    async def get_secret(self, key: str, default: Any = None) -> Optional[str]:
        """Get secret from environment variables."""
        return os.getenv(key, default)

    async def set_secret(self, key: str, value: str) -> None:
        """Set environment variable (not recommended for production)."""
        os.environ[key] = value

    async def delete_secret(self, key: str) -> None:
        """Delete environment variable."""
        if key in os.environ:
            del os.environ[key]

    async def list_secrets(self, prefix: str = "") -> Dict[str, str]:
        """List environment variables with prefix."""
        return {
            k: v for k, v in os.environ.items()
            if k.startswith(prefix)
        }


class VaultProvider(SecretsProvider):
    """HashiCorp Vault secrets provider."""

    def __init__(
        self,
        url: str = "http://localhost:8200",
        token: Optional[str] = None,
        mount_point: str = "secret",
        **kwargs
    ):
        self.url = url
        self.token = token or os.getenv("VAULT_TOKEN")
        self.mount_point = mount_point
        self.client = None

        if self.token:
            self.client = hvac.Client(url=url, token=self.token)

    async def _ensure_client(self):
        """Ensure Vault client is initialized."""
        if self.client is None:
            if not self.token:
                raise ValueError("Vault token not provided")
            self.client = hvac.Client(url=self.url, token=self.token)

        if not self.client.is_authenticated():
            raise ValueError("Vault client not authenticated")

    async def get_secret(self, key: str, default: Any = None) -> Optional[str]:
        """Get secret from Vault."""
        try:
            await self._ensure_client()
            response = self.client.secrets.kv.v2.read_secret_version(
                path=key,
                mount_point=self.mount_point
            )
            return response["data"]["data"].get(key.split("/")[-1])
        except Exception:
            return default

    async def set_secret(self, key: str, value: str) -> None:
        """Set secret in Vault."""
        await self._ensure_client()
        self.client.secrets.kv.v2.create_or_update_secret_version(
            path=key,
            secret={key.split("/")[-1]: value},
            mount_point=self.mount_point
        )

    async def delete_secret(self, key: str) -> None:
        """Delete secret from Vault."""
        await self._ensure_client()
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=key,
            mount_point=self.mount_point
        )

    async def list_secrets(self, prefix: str = "") -> Dict[str, str]:
        """List secrets with prefix."""
        await self._ensure_client()
        try:
            response = self.client.secrets.kv.v2.list_secrets_version(
                path=prefix,
                mount_point=self.mount_point
            )
            secrets = {}
            for secret_key in response["data"]["keys"]:
                full_key = f"{prefix}/{secret_key}".strip("/")
                value = await self.get_secret(full_key)
                if value:
                    secrets[full_key] = value
            return secrets
        except Exception:
            return {}


class AWSSecretsProvider(SecretsProvider):
    """AWS Secrets Manager provider."""

    def __init__(self, region_name: str = "us-east-1", **kwargs):
        self.region_name = region_name
        self.client = boto3.client("secretsmanager", region_name=region_name)

    async def get_secret(self, key: str, default: Any = None) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=key)
            return response["SecretString"]
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return default
            raise
        except Exception:
            return default

    async def set_secret(self, key: str, value: str) -> None:
        """Set secret in AWS Secrets Manager."""
        try:
            # Try to update existing secret
            self.client.update_secret(SecretId=key, SecretString=value)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Create new secret
                self.client.create_secret(Name=key, SecretString=value)
            else:
                raise

    async def delete_secret(self, key: str) -> None:
        """Delete secret from AWS Secrets Manager."""
        self.client.delete_secret(SecretId=key, ForceDeleteWithoutRecovery=True)

    async def list_secrets(self, prefix: str = "") -> Dict[str, str]:
        """List secrets with prefix."""
        secrets = {}
        paginator = self.client.get_paginator("list_secrets")

        for page in paginator.paginate():
            for secret in page["SecretList"]:
                name = secret["Name"]
                if name.startswith(prefix):
                    value = await self.get_secret(name)
                    if value:
                        secrets[name] = value

        return secrets
