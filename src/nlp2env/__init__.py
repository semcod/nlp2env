"""nlp2env — read/write .env files for agent and MCP workflows."""

from nlp2env.env_file import EnvFile, mask_value
from nlp2env.profiles import EMAIL_PROFILE_KEYS, email_profile_from_dict

__all__ = [
    "EnvFile",
    "mask_value",
    "EMAIL_PROFILE_KEYS",
    "email_profile_from_dict",
]

__version__ = "0.1.1"
