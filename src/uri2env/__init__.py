"""URI → .env materialization (env:// scheme)."""

from uri2env.materialize import MaterializeResult, materialize_uri
from uri2env.resolve import resolve_prompt_to_env_uri
from uri2env.uri import (
    ENV_SCHEME,
    build_env_uri_index,
    is_env_uri,
    uri_for_env_file,
    uri_for_getv_profile,
    uri_for_getv_var,
    uri_for_nlp2env_profile,
)

__all__ = [
    "ENV_SCHEME",
    "MaterializeResult",
    "build_env_uri_index",
    "is_env_uri",
    "materialize_uri",
    "resolve_prompt_to_env_uri",
    "uri_for_env_file",
    "uri_for_getv_profile",
    "uri_for_getv_var",
    "uri_for_nlp2env_profile",
]
