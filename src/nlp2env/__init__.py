"""nlp2env — read/write .env files for agent and MCP workflows."""

from nlp2env.env_file import EnvFile, mask_value
from nlp2env.profiles import EMAIL_PROFILE_KEYS, email_profile_from_dict

__all__ = [
    "EnvFile",
    "mask_value",
    "EMAIL_PROFILE_KEYS",
    "email_profile_from_dict",
]

__version__ = "0.1.6"

# Re-export uri2env for nlp2uri integration
try:
    from uri2env import materialize_uri, uri_for_nlp2env_profile  # noqa: F401
except ImportError:
    pass
