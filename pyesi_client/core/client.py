"""
Professional EVE Online ESI Client

Built on pyesi-openapi with intelligent token management, caching, and utilities.
"""

import urllib3
import logging
from datetime import datetime

from pyesi_openapi import (
    AllianceApi,
    ApiClient,
    AssetsApi,
    CalendarApi,
    CharacterApi,
    ClonesApi,
    Configuration,
    ContactsApi,
    ContractsApi,
    CorporationApi,
    DogmaApi,
    FactionWarfareApi,
    FittingsApi,
    FleetsApi,
    IncursionsApi,
    IndustryApi,
    InsuranceApi,
    KillmailsApi,
    LocationApi,
    LoyaltyApi,
    MailApi,
    MarketApi,
    PlanetaryInteractionApi,
    RoutesApi,
    SearchApi,
    SkillsApi,
    SovereigntyApi,
    StatusApi,
    UniverseApi,
    UserInterfaceApi,
    WalletApi,
    WarsApi,
)

from pyesi_client.constants import (
    DEFAULT_ESI_AGENT,
    DEFAULT_ESI_HOST,
    DEFAULT_MAX_RETRIES,
    EsiScope,
    DEFAULT_BACKOFF_MAX,
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_BACKOFF_JITTER,
)
from pyesi_client.core.auth import EsiAuth
from pyesi_client.core.scope_manager import EsiScopeManager
from pyesi_client.models import EsiJwtTokenData

logger = logging.getLogger(__name__)


class EsiClient:
    """
    Professional EVE Online ESI client with automatic token management.

    Features:
    - Automatic token refresh
    - Built-in ESI compatibility date handling
    - Lazy API endpoint initialization
    - Intelligent error handling
    """

    # Current ESI compatibility date
    COMPATIBILITY_DATE = datetime(2025, 8, 26)

    def __init__(
        self,
        client_id: str,
        *,
        client_secret: str | None = None,
        redirect_uri: str = "http://localhost",
        scopes: list[EsiScope] | None = None,
        user_agent: str = DEFAULT_ESI_AGENT,
        timeout: int = 30,
        retry: urllib3.Retry | int | None = urllib3.Retry(
            total=DEFAULT_MAX_RETRIES,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            backoff_jitter=DEFAULT_BACKOFF_JITTER,
            backoff_max=DEFAULT_BACKOFF_MAX,
        ),
        host: str = DEFAULT_ESI_HOST,
    ):
        """
        Initialize ESI client.

        Args:
            client_id: EVE application client ID
            client_secret: EVE application client secret (optional for PKCE)
            redirect_uri: OAuth redirect URI
            scopes: Required ESI scopes
            user_agent: Custom user agent
            timeout: Request timeout in seconds
            retries: urllib3.Retry
            host: ESI API base URL
            refresh_token: OAuth immortal refresh token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # Configure OpenAPI client
        self._setup_api_client(host, user_agent, timeout, retry)

        # Initialize scope manager
        self.scope_manager = EsiScopeManager(scopes=set(scopes or []))

        # Initialize auth handler
        self.auth = EsiAuth(
            api_client=self.api_client,
            scope_manager=self.scope_manager,
            redirect_uri=redirect_uri,
            client_id=client_id,
            client_secret=client_secret,
        )

        self._alliance_api: AllianceApi | None = None
        self._assets_api: AssetsApi | None = None
        self._calendar_api: CalendarApi | None = None
        self._character_api: CharacterApi | None = None
        self._clones_api: ClonesApi | None = None
        self._contacts_api: ContactsApi | None = None
        self._contracts_api: ContractsApi | None = None
        self._corporation_api: CorporationApi | None = None
        self._dogma_api: DogmaApi | None = None
        self._faction_warfare_api: FactionWarfareApi | None = None
        self._fittings_api: FittingsApi | None = None
        self._fleets_api: FleetsApi | None = None
        self._incursions_api: IncursionsApi | None = None
        self._industry_api: IndustryApi | None = None
        self._insurance_api: InsuranceApi | None = None
        self._killmails_api: KillmailsApi | None = None
        self._location_api: LocationApi | None = None
        self._loyalty_api: LoyaltyApi | None = None
        self._mail_api: MailApi | None = None
        self._market_api: MarketApi | None = None
        self._planetary_interaction_api: PlanetaryInteractionApi | None = None
        self._routes_api: RoutesApi | None = None
        self._search_api: SearchApi | None = None
        self._skills_api: SkillsApi | None = None
        self._sovereignty_api: SovereigntyApi | None = None
        self._status_api: StatusApi | None = None
        self._universe_api: UniverseApi | None = None
        self._user_interface_api: UserInterfaceApi | None = None
        self._wallet_api: WalletApi | None = None
        self._wars_api: WarsApi | None = None

        logger.info(f"EsiClient initialized for client_id: {client_id}")
        self._api_ns = None

    def _setup_api_client(
        self, host: str, user_agent: str | None, timeout: int, retry: urllib3.Retry | int | None
    ) -> None:
        """Configure the underlying API client."""
        self.config = Configuration(
            host=host,
            retries=retry,  # type: ignore
        )

        if user_agent:
            self.config.user_agent = user_agent

        # Configure timeout
        self.config.socket_timeout = timeout
        self.config.connection_timeout = timeout

        self.api_client = ApiClient(self.config)

    def _update_access_token(self) -> None:
        """Update API client with current access token."""
        try:
            token = self.auth.access_token
            self.config.access_token = token
            logger.debug("Access token updated")
        except Exception as e:
            raise ValueError(f"Failed to get access token: {e}") from e

    def get_auth_url(self, *, state: str | None = None) -> str:
        """Get OAuth authorization URL."""
        auth_data = self.auth.create_auth_url(state=state)
        return auth_data.url

    def authenticate(self, authorization_code: str) -> None:
        """
        Complete OAuth flow with authorization code.

        Args:
            authorization_code: Code from OAuth callback
        """
        try:
            self.auth.exchange_code(authorization_code)
            self._update_access_token()
            logger.info("Authentication successful")
        except Exception as e:
            raise ValueError(f"Authentication failed: {e}") from e

    def authenticate_refresh_token(self, refresh_token: str) -> None:
        """
        Set refresh token for existing authentication.

        Args:
            refresh_token: Valid EVE SSO refresh token
        """
        try:
            self.auth.refresh(refresh_token)
            self._update_access_token()
            logger.info("Token refreshed successfully")
        except Exception as e:
            raise ValueError(f"Token refresh failed: {e}") from e

    def verify_token(self) -> EsiJwtTokenData:
        """Verify current token and get character info."""
        try:
            jwt_data = self.auth.verify()
            return jwt_data
        except Exception as e:
            raise ValueError(f"Token verification failed: {e}") from e

    def add_scopes(self, *scopes: EsiScope) -> None:
        """Add scopes to the client (requires re-authentication)."""
        self.scope_manager.add(*scopes)
        logger.info(f"Added scopes: {[s.value for s in scopes]}")

    def get_required_scopes(self) -> list[str]:
        """Get list of currently required scopes."""
        return [scope.value for scope in self.scope_manager.scopes]

    @property
    def is_authenticated(self) -> bool:
        """Check if client has valid authentication."""
        try:
            self.auth.access_token
            return True
        except Exception:
            return False

    @property
    def compatibility_date(self) -> datetime:
        """Get current ESI compatibility date."""
        return self.COMPATIBILITY_DATE

    @property
    def alliance(self) -> AllianceApi:
        """Alliance API endpoints"""
        if self._alliance_api is None:
            self._alliance_api = AllianceApi(self.api_client)
        return self._alliance_api

    @property
    def assets(self) -> AssetsApi:
        """Assets API endpoints"""
        if self._assets_api is None:
            self._assets_api = AssetsApi(self.api_client)
        return self._assets_api

    @property
    def calendar(self) -> CalendarApi:
        """Calendar API endpoints"""
        if self._calendar_api is None:
            self._calendar_api = CalendarApi(self.api_client)
        return self._calendar_api

    @property
    def character(self) -> CharacterApi:
        """Character API endpoints"""
        if self._character_api is None:
            self._character_api = CharacterApi(self.api_client)
        return self._character_api

    @property
    def clones(self) -> ClonesApi:
        """Clones API endpoints"""
        if self._clones_api is None:
            self._clones_api = ClonesApi(self.api_client)
        return self._clones_api

    @property
    def contacts(self) -> ContactsApi:
        """Contacts API endpoints"""
        if self._contacts_api is None:
            self._contacts_api = ContactsApi(self.api_client)
        return self._contacts_api

    @property
    def contracts(self) -> ContractsApi:
        """Contracts API endpoints"""
        if self._contracts_api is None:
            self._contracts_api = ContractsApi(self.api_client)
        return self._contracts_api

    @property
    def corporation(self) -> CorporationApi:
        """Corporation API endpoints"""
        if self._corporation_api is None:
            self._corporation_api = CorporationApi(self.api_client)
        return self._corporation_api

    @property
    def dogma(self) -> DogmaApi:
        """Dogma API endpoints"""
        if self._dogma_api is None:
            self._dogma_api = DogmaApi(self.api_client)
        return self._dogma_api

    @property
    def faction_warfare(self) -> FactionWarfareApi:
        """FactionWarfare API endpoints"""
        if self._faction_warfare_api is None:
            self._faction_warfare_api = FactionWarfareApi(self.api_client)
        return self._faction_warfare_api

    @property
    def fittings(self) -> FittingsApi:
        """Fittings API endpoints"""
        if self._fittings_api is None:
            self._fittings_api = FittingsApi(self.api_client)
        return self._fittings_api

    @property
    def fleets(self) -> FleetsApi:
        """Fleets API endpoints"""
        if self._fleets_api is None:
            self._fleets_api = FleetsApi(self.api_client)
        return self._fleets_api

    @property
    def incursions(self) -> IncursionsApi:
        """Incursions API endpoints"""
        if self._incursions_api is None:
            self._incursions_api = IncursionsApi(self.api_client)
        return self._incursions_api

    @property
    def industry(self) -> IndustryApi:
        """Industry API endpoints"""
        if self._industry_api is None:
            self._industry_api = IndustryApi(self.api_client)
        return self._industry_api

    @property
    def insurance(self) -> InsuranceApi:
        """Insurance API endpoints"""
        if self._insurance_api is None:
            self._insurance_api = InsuranceApi(self.api_client)
        return self._insurance_api

    @property
    def killmails(self) -> KillmailsApi:
        """Killmails API endpoints"""
        if self._killmails_api is None:
            self._killmails_api = KillmailsApi(self.api_client)
        return self._killmails_api

    @property
    def location(self) -> LocationApi:
        """Location API endpoints"""
        if self._location_api is None:
            self._location_api = LocationApi(self.api_client)
        return self._location_api

    @property
    def loyalty(self) -> LoyaltyApi:
        """Loyalty API endpoints"""
        if self._loyalty_api is None:
            self._loyalty_api = LoyaltyApi(self.api_client)
        return self._loyalty_api

    @property
    def mail(self) -> MailApi:
        """Mail API endpoints"""
        if self._mail_api is None:
            self._mail_api = MailApi(self.api_client)
        return self._mail_api

    @property
    def market(self) -> MarketApi:
        """Market API endpoints"""
        if self._market_api is None:
            self._market_api = MarketApi(self.api_client)
        return self._market_api

    @property
    def planetary_interaction(self) -> PlanetaryInteractionApi:
        """PlanetaryInteraction API endpoints"""
        if self._planetary_interaction_api is None:
            self._planetary_interaction_api = PlanetaryInteractionApi(self.api_client)
        return self._planetary_interaction_api

    @property
    def routes(self) -> RoutesApi:
        """Routes API endpoints"""
        if self._routes_api is None:
            self._routes_api = RoutesApi(self.api_client)
        return self._routes_api

    @property
    def search(self) -> SearchApi:
        """Search API endpoints"""
        if self._search_api is None:
            self._search_api = SearchApi(self.api_client)
        return self._search_api

    @property
    def skills(self) -> SkillsApi:
        """Skills API endpoints"""
        if self._skills_api is None:
            self._skills_api = SkillsApi(self.api_client)
        return self._skills_api

    @property
    def sovereignty(self) -> SovereigntyApi:
        """Sovereignty API endpoints"""
        if self._sovereignty_api is None:
            self._sovereignty_api = SovereigntyApi(self.api_client)
        return self._sovereignty_api

    @property
    def status(self) -> StatusApi:
        """Status API endpoints"""
        if self._status_api is None:
            self._status_api = StatusApi(self.api_client)
        return self._status_api

    @property
    def universe(self) -> UniverseApi:
        """Universe API endpoints"""
        if self._universe_api is None:
            self._universe_api = UniverseApi(self.api_client)
        return self._universe_api

    @property
    def user_interface(self) -> UserInterfaceApi:
        """UserInterface API endpoints"""
        if self._user_interface_api is None:
            self._user_interface_api = UserInterfaceApi(self.api_client)
        return self._user_interface_api

    @property
    def wallet(self) -> WalletApi:
        """Wallet API endpoints"""
        if self._wallet_api is None:
            self._wallet_api = WalletApi(self.api_client)
        return self._wallet_api

    @property
    def wars(self) -> WarsApi:
        """Wars API endpoints"""
        if self._wars_api is None:
            self._wars_api = WarsApi(self.api_client)
        return self._wars_api

    @property
    def api(self):
        """Typed API namespace providing auto-compat subclasses of generated APIs.

        Usage: client.api.alliance.get_alliances()  # x_compatibility_date auto-injected
        """
        if self._api_ns is None:
            # Lazy import to avoid cycles
            from pyesi_client.core.autoapi import build_api_namespace

            self._api_ns = build_api_namespace(self)
        return self._api_ns

    def call_api(self, func):
        res = func
        if "headers" in res:
            etag = res["headers"]["Etag"]
            print(etag)
        if "data" in res:
            return res["data"]
        return res
