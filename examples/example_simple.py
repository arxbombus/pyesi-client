# Regional trader script that takes in a list of inputs (products), along with two station/citadels, and a base shipping cost per m3.
# It outputs the following for each product: sell/buy price at station 1, sell/buy price at station2, margins if I were to place buy orders or buy from sell orders at one and ship to the other, and vice versa.
# It should output this in a nice, structured manner.


from pyesi_client import EsiScope, EsiScopeManager
from pyesi_client.core.client import EsiClient


CLIENT_ID = "7704f80cb19a403abf1a1b8c4d184bc5"
EVE_CLIENT_SECRET = "DcUSHfWjQSP3hVHmDJNaCBtC5zpYfVnXmgvSTHH1"
REFRESH_TOKEN = "SZyChGGgM0WU3BePCG4G9g=="  # if you have a refresh token, use it to reauthenticate the user


# class EsiResponse(BaseModel):
#     etag: str  # Etag
#     compatibility_date: datetime  # X-Compatibility-Date
#     is_cache_hit: bool  # X-Esi-Cache-Status = "HIT" | "MISS"
#     error_limit_remain: int  # X-Esi-Error-Limit-Remain
#     error_limit_reset: int  # X-Esi-Error-Limit-Reset
#     request_id: str  # X-Esi-Request-Id
#     pages: int | None  # X-Pages

#     @field_validator("is_cache_hit")
#     def validate_cache_hit_status(self, v):
#         return v == "HIT"


scope_manager = EsiScopeManager()
client = EsiClient(
    CLIENT_ID,
    scopes=EsiScope.all_values(),
)

res = client.call_api(client.alliance.get_alliances_with_http_info(x_compatibility_date=client.COMPATIBILITY_DATE))
print(res)

# Typed auto-compat usage (no explicit compatibility date):
res2 = client.api.alliance.get_alliances()
print(res2)
# public endpoints now work
# alliances = client.alliance.get_alliances(client.compatibility_date)
# print(alliances)
# res = client.alliance.get_alliances_with_http_info(
#     client.compatibility_date
# )  # use with http_info to get access to things like headers
# print(res.headers)


# if not client.is_authenticated:
#     if REFRESH_TOKEN:
#         print("Authenticating with refresh token using client.authenticate_refresh_token")
#         client.authenticate_refresh_token(REFRESH_TOKEN)
#     else:
#         print("Redirecting to EVE SSO Login page")
#         auth_url = client.get_auth_url()
#         webbrowser.open(auth_url)
# # if user authed, they can give us an access code
# # code = input("Enter your authorization code: ")
# # client.authenticate(code)
# print(f"Refresh Token: {client.auth.refresh_token}")
# token_data = client.verify_token()
# print(f"Authenticated: {token_data.character_name} (ID {token_data.character_id})")

# # Now that we're authed, we can use private endpoints as well
# # Find keepstar structure that has character on ACL
# structure_search = client.search.get_characters_character_id_search(
#     ["structure"], token_data.character_id, "1st Taj Mahgoon", client.compatibility_date
# )
# keepstar_id = structure_search.structure[0] if structure_search.structure else None
# print(f"Keepstar Structure ID: {keepstar_id}")

# if keepstar_id:
#     res = client.market.get_markets_structures_structure_id_with_http_info(keepstar_id, client.compatibility_date)
#     print(res.headers)
#     print(res.data[-10])
#     headers = res.headers
#     etag = None
#     if headers:
#         etag = headers.get("Etag", None)
#     res = client.market.get_markets_structures_structure_id_with_http_info(
#         keepstar_id, client.compatibility_date, page=2, _headers={"Etag": etag} if etag else None
#     )
#     print(res.headers)
#     print(res.data[-10])
