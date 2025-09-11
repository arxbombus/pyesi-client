"""
EVE Online ESI client library built on pyesi-openapi with caching and utilities.

This library provides a higher-level interface to the EVE Online ESI API,
built on top of the generated pyesi-openapi client with added features like
caching, rate limiting, and utility functions.
"""

__version__ = "0.1.0"

from pyesi_client.constants import EsiScope
from pyesi_client.core import EsiAuth, EsiClient, EsiMetadataManager, EsiScopeManager

__all__ = ["EsiAuth", "EsiClient", "EsiMetadataManager", "EsiScopeManager", "EsiScope"]
