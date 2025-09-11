from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable, Type, TypeVar, cast

# We depend on the generated API classes only for typing inheritance. They are imported in client.py.

T = TypeVar("T")


def _wrap_method_with_compat(method: Callable[..., Any], compat_date_provider: Callable[[], Any]) -> Callable[..., Any]:
    """Return a wrapper that injects x_compatibility_date if the parameter exists and wasn't provided."""
    sig = None
    try:
        sig = inspect.signature(method)
    except (TypeError, ValueError):
        # Builtins or C-accelerated callables may not have signatures; return method unchanged
        return method

    params = sig.parameters
    expects_compat = "x_compatibility_date" in params

    if not expects_compat:
        return method

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "x_compatibility_date" not in kwargs:
            kwargs["x_compatibility_date"] = compat_date_provider()
        return method(*args, **kwargs)

    # Preserve metadata as best-effort
    try:
        wrapper.__name__ = getattr(method, "__name__", wrapper.__name__)
        wrapper.__doc__ = getattr(method, "__doc__", wrapper.__doc__)
    except Exception:
        pass
    return wrapper


class _AutoCompatBase:
    """
    Mixin providing attribute wrapping for generated API classes to auto-inject x_compatibility_date.

    Assumptions:
    - The concrete subclass inherits from a generated API class (e.g., AllianceApi).
    - Instance has _compat_date_provider: Callable[[], Any]
    """

    def __init__(self, *args: Any, _compat_date_provider: Callable[[], Any], **kwargs: Any) -> None:  # type: ignore[override]
        super().__init__(*args, **kwargs)  # type: ignore[misc]
        self._compat_date_provider = _compat_date_provider

    def __getattribute__(self, name: str) -> Any:
        # Bypass wrapping for internals
        if name.startswith("_"):
            return super().__getattribute__(name)  # type: ignore[misc]

        attr = super().__getattribute__(name)  # type: ignore[misc]
        if callable(attr):
            return _wrap_method_with_compat(cast(Callable[..., Any], attr), self._compat_date_provider)
        return attr


def create_autocompat_instance(
    base_cls: Type[T],
    *args: Any,
    compat_date_provider: Callable[[], Any],
    **kwargs: Any,
) -> T:
    """
    Create an instance of a typed subclass of the given generated API class that auto-injects
    x_compatibility_date when omitted.

    Returns an instance that is a true subclass of base_cls, so IDEs preserve method names/signatures.
    """
    # Dynamically create a subclass combining the mixin with the generated base class
    subclass_name = f"AutoCompat_{base_cls.__name__}"
    AutoClass = cast(Type[T], type(subclass_name, (_AutoCompatBase, base_cls), {}))
    return AutoClass(*args, _compat_date_provider=compat_date_provider, **kwargs)  # type: ignore


def build_api_namespace(client: Any) -> SimpleNamespace:
    """Build a namespace with attributes for each generated API bound to the client's ApiClient.

    This returns an object with attributes like alliance, market, etc., each being a typed
    AutoCompat subclass instance of the corresponding generated API class.
    """
    from pyesi_openapi import (
        AllianceApi,
        AssetsApi,
        CalendarApi,
        CharacterApi,
        ClonesApi,
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

    # Default compatibility date provider reads from the client at call-time
    def compat_provider():
        return client.compatibility_date

    ns = SimpleNamespace(
        alliance=create_autocompat_instance(AllianceApi, client.api_client, compat_date_provider=compat_provider),
        assets=create_autocompat_instance(AssetsApi, client.api_client, compat_date_provider=compat_provider),
        calendar=create_autocompat_instance(CalendarApi, client.api_client, compat_date_provider=compat_provider),
        character=create_autocompat_instance(CharacterApi, client.api_client, compat_date_provider=compat_provider),
        clones=create_autocompat_instance(ClonesApi, client.api_client, compat_date_provider=compat_provider),
        contacts=create_autocompat_instance(ContactsApi, client.api_client, compat_date_provider=compat_provider),
        contracts=create_autocompat_instance(ContractsApi, client.api_client, compat_date_provider=compat_provider),
        corporation=create_autocompat_instance(CorporationApi, client.api_client, compat_date_provider=compat_provider),
        dogma=create_autocompat_instance(DogmaApi, client.api_client, compat_date_provider=compat_provider),
        faction_warfare=create_autocompat_instance(
            FactionWarfareApi, client.api_client, compat_date_provider=compat_provider
        ),
        fittings=create_autocompat_instance(FittingsApi, client.api_client, compat_date_provider=compat_provider),
        fleets=create_autocompat_instance(FleetsApi, client.api_client, compat_date_provider=compat_provider),
        incursions=create_autocompat_instance(IncursionsApi, client.api_client, compat_date_provider=compat_provider),
        industry=create_autocompat_instance(IndustryApi, client.api_client, compat_date_provider=compat_provider),
        insurance=create_autocompat_instance(InsuranceApi, client.api_client, compat_date_provider=compat_provider),
        killmails=create_autocompat_instance(KillmailsApi, client.api_client, compat_date_provider=compat_provider),
        location=create_autocompat_instance(LocationApi, client.api_client, compat_date_provider=compat_provider),
        loyalty=create_autocompat_instance(LoyaltyApi, client.api_client, compat_date_provider=compat_provider),
        mail=create_autocompat_instance(MailApi, client.api_client, compat_date_provider=compat_provider),
        market=create_autocompat_instance(MarketApi, client.api_client, compat_date_provider=compat_provider),
        planetary_interaction=create_autocompat_instance(
            PlanetaryInteractionApi, client.api_client, compat_date_provider=compat_provider
        ),
        routes=create_autocompat_instance(RoutesApi, client.api_client, compat_date_provider=compat_provider),
        search=create_autocompat_instance(SearchApi, client.api_client, compat_date_provider=compat_provider),
        skills=create_autocompat_instance(SkillsApi, client.api_client, compat_date_provider=compat_provider),
        sovereignty=create_autocompat_instance(SovereigntyApi, client.api_client, compat_date_provider=compat_provider),
        status=create_autocompat_instance(StatusApi, client.api_client, compat_date_provider=compat_provider),
        universe=create_autocompat_instance(UniverseApi, client.api_client, compat_date_provider=compat_provider),
        user_interface=create_autocompat_instance(
            UserInterfaceApi, client.api_client, compat_date_provider=compat_provider
        ),
        wallet=create_autocompat_instance(WalletApi, client.api_client, compat_date_provider=compat_provider),
        wars=create_autocompat_instance(WarsApi, client.api_client, compat_date_provider=compat_provider),
    )

    return ns
