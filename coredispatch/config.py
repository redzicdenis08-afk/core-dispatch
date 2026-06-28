"""Configuration for a dispatch deployment.

Secrets are never stored in config. Config only holds the *names* of the
environment variables that carry secrets, and resolves them at runtime.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DispatchConfig:
    tenant: str = "default"
    plan_amount_cents: int = 14900
    max_attempts: int = 4
    script: str = ""
    # Names of env vars that hold secrets. The values never live in config files.
    voice_api_key_env: str = "VOICE_API_KEY"
    webhook_secret_env: str = "DISPATCH_WEBHOOK_SECRET"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DispatchConfig":
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def resolve_secret(self, env_name: str) -> str:
        """Read a secret from the environment by name. Empty string if unset."""
        return os.environ.get(env_name, "")
