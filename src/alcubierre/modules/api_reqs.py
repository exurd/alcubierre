# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/api_reqs.py
"""
Request handling for alcubierre.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import math
import random
import requests
import time

from alcubierre.modules import data_save
from alcubierre.modules.verbose_print import vPrint, vvPrint, log_n_print, error_n_print

RESPONSE_CACHE = {}
USING_PERM_CACHE = False


def get_perm_cache():
    """
    Get response cache from pickled file.
    """
    global USING_PERM_CACHE
    global RESPONSE_CACHE

    USING_PERM_CACHE = True
    perm_response_cache = data_save.load_data("responseCache.pickle", as_dict=True)
    if perm_response_cache == {}:
        return
    RESPONSE_CACHE = perm_response_cache


def save_to_perm_cache(url, response, cache_results=True) -> requests.Response:
    """
    Saves response to pickled file.
    """
    response.request.headers = None  # stops cookies from being saved into the pickle
    if cache_results:
        RESPONSE_CACHE[url] = response
        if USING_PERM_CACHE:
            data_save.save_data(RESPONSE_CACHE, "responseCache.pickle")
    return response


request_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=5)
request_session.mount("https://", adapter)
request_session.mount("http://", adapter)


def init(user_agent=None, rbx_token=None):
    """
    Initializes the request session with user agent and cookies.
    """
    if user_agent is not None:
        request_session.headers["User-Agent"] = str(user_agent)

    if rbx_token is not None:
        request_session.cookies[".ROBLOSECURITY"] = str(rbx_token)
    else:
        print("Warning: Ecomony API is limited to 1 request per minute!\n"
              "Place playability info is unavailable!\n"
              "Adding your Roblox token is highly recommended!")


def is_token_cookie_there() -> bool:
    """
    Returns True if the .ROBLOSECURITY cookie is in the request session.
    """
    return ".ROBLOSECURITY" in request_session.cookies


def get_request_url(url, retry_amount=8, accept_forbidden=False, accept_not_found=True, initial_wait_time=None, cache_results=True) -> requests.Response:
    """
    Internal function to request urls.
    """
    if not isinstance(url, str):
        vPrint("getRequestURL: url was not string type, sending None")
        return None
    if cache_results and url in RESPONSE_CACHE:
        vvPrint(f"Found response for {url} in cache.")
        return RESPONSE_CACHE[url]

    tries = 0
    vPrint(f"Requesting {url}...")
    for _ in range(retry_amount):
        vvPrint(f"Attempt {tries}...")
        tries += 1
        try:
            response = request_session.get(url)
            vPrint(f"Response Status Code: {response.status_code}")
            sc = response.status_code
            if sc in (200, 302):
                return save_to_perm_cache(url, response, cache_results)  # OK, Found
            if accept_forbidden and sc == 403:
                return save_to_perm_cache(url, response, cache_results)  # Forbidden (if acceptForbidden)
            if accept_not_found and sc == 404:
                return save_to_perm_cache(url, response, cache_results)  # Not Found (if acceptNotFound)
            if sc == 410:
                return save_to_perm_cache(url, response, cache_results)  # Gone
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            vPrint("Timed out!")
            vPrint(f"Request failed: {e}")
        except requests.exceptions.TooManyRedirects as e:
            vPrint("Too many redirects!")
            vPrint(f"Request failed: {e}")
            return False
        except requests.exceptions.HTTPError:
            if sc == 403 or sc == 419:  # Forbidden (Roblox sends 403 for some requests that need a CSRF token), Page Expired
                vPrint("Token Validation Failed. Re-validating...")
                validate_csrf()
            elif sc == 400:
                return False  # Bad Request
            elif sc == 429:  # Too Many Requests
                vPrint("Too many requests!")
        except requests.exceptions.RequestException as e:
            vPrint(f"Request failed: {e}")
            return False
        if tries < retry_amount:
            sleep_time = random.randint(
                math.floor(2 ** (tries - 0.5)),
                math.floor(2 ** tries)
                )
            if initial_wait_time is not None:
                sleep_time = int(initial_wait_time)
                initial_wait_time = None
            error_n_print(f"Something happened when trying to get [{url}]!")
            log_n_print(f"Sleeping {sleep_time} seconds...")
            time.sleep(sleep_time)
    return False


def validate_csrf() -> str:
    """
    Gets X-CSRF-Token for Roblox.
    """
    req = requests.post(url="https://auth.roblox.com/v2/logout", timeout=60)
    return req.headers["X-CSRF-Token"]


def get_economy_info(asset_id, act_like_place_details_api=False) -> dict:
    """
    Get economy information from asset ID. Guest users have a long rate limit.
    Optional setting allows for this to act like place details api.

    Example JSON:
    {
        "TargetId": 0,
        "ProductType": null,
        "AssetId": 123456,
        "ProductId": 0,
        "Name": "blackcatgoth"s Place",
        "Description": "",
        "AssetTypeId": 9,
        "Creator": {
            "Id": 52988,
            "Name": "blackcatgoth",
            "CreatorType": "User",
            "CreatorTargetId": 52988,
            "HasVerifiedBadge": false
        },
        "IconImageAssetId": 752403374,
        "Created": "2007-08-27T17: 40: 45.12Z",
        "Updated": "2007-08-27T17: 40: 45.12Z",
        "PriceInRobux": null,
        "PriceInTickets": null,
        "Sales": 0,
        "IsNew": false,
        "IsForSale": false,
        "IsPublicDomain": false,
        "IsLimited": false,
        "IsLimitedUnique": false,
        "Remaining": null,
        "MinimumMembershipLevel": 0,
        "ContentRatingTypeId": 0,
        "SaleAvailabilityLocations": null,
        "SaleLocation": null,
        "CollectibleItemId": null,
        "CollectibleProductId": null,
        "CollectiblesItemDetails": null
    }
    """
    economy_check = get_request_url(f"https://economy.roblox.com/v2/assets/{str(asset_id)}/details", initial_wait_time=60)
    if economy_check.ok:
        economy_json = economy_check.json()
        if "errors" in economy_json:
            error_n_print(f"Error in economy_json! [{economy_json}]")
            return False
        vvPrint(f"economy_json: [{economy_json}]")
        if act_like_place_details_api:
            return {k.lower(): v for k, v in economy_json.items()}
        return economy_json
    return False


def get_place_info(place_id, no_alternative=False) -> dict:
    """
    Gets place information from place ID.
    Guest users cannot use this API. If `no_alternative` is False, then the economy api will be used instead.

    Example JSON:
    {
        "placeId": 20876709,
        "name": "[ Content Deleted ]",
        "description": "[ Content Deleted ]",
        "sourceName": "[ Content Deleted ]",
        "sourceDescription": "[ Content Deleted ]",
        "url": "https://www.roblox.com/games/20876709/Content-Deleted",
        "builder": "Chevsterr",
        "builderId": 6128452,
        "hasVerifiedBadge": False,
        "isPlayable": False,
        "reasonProhibited": "AssetUnapproved",
        "universeId": 19043203,
        "universeRootPlaceId": 20876709,
        "price": 0,
        "imageToken": "T_20876709_5455"
    }
    """
    if is_token_cookie_there():
        place_check = get_request_url(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={str(place_id)}")
        if place_check.ok:
            place_json = place_check.json()
            if "errors" in place_json:
                error_n_print(f"Error in place_json! [{place_json}]")
                return False
            vvPrint(f"place_json: [{place_json}]")
            return place_json[0]
        return False

    if not no_alternative:
        vPrint("multiget-place-details is unusable, but alternative is allowed.")
        vPrint("Using economy API with compatability-esque keys...")
        return get_economy_info(place_id, act_like_place_details_api=True)

    vPrint("multiget-place-details is unusable; cannot use economy api. Returning false.")
    return False


def get_badge_info(badge_id) -> dict:
    """
    Gets badge information from badge ID.

    Example JSON:
    {
        "id": 14427263,
        "name": "Juice Tycoon Money Player Badge",
        "description": "Go On My Juice Tycoon To Earn This!!!",
        "displayName": "Juice Tycoon Money Player Badge",
        "displayDescription": "Go On My Juice Tycoon To Earn This!!!",
        "enabled": True,
        "iconImageId": 14426818,
        "displayIconImageId": 14426818,
        "created": "2009-08-13T07:56:44.337-05:00",
        "updated": "2015-12-21T15:09:14.887-06:00",
        "statistics": {
            "pastDayAwardedCount": 0,
            "awardedCount": 1756,
            "winRatePercentage": 0.0
        },
        "awardingUniverse": {
            "id": 685746,
            "name": "JUICE TYCOON!! YOU CAN EARN A BADGE HERE!!!!",
            "rootPlaceId": 4285089
        }
    }

    Example error:
    {
        "errors": [
            {
                "code": 1,
                "message": "Badge is invalid or does not exist.",
                "userFacingMessage": "Something went wrong"
            }
        ]
    }
    """
    badge_check = get_request_url(f"https://badges.roblox.com/v1/badges/{str(badge_id)}")
    if badge_check.ok:
        badge_json = badge_check.json()
        if "errors" in badge_json:
            error_n_print(f"Error in badge_json! [{badge_json}]")
            return False
        vvPrint(f"badge_json: [{badge_json}]")
        return badge_json
    return False


def get_universe_info(universe_id) -> dict:
    """
    Gets universe information from universe ID.

    Example JSON:
    {
        "data": [
            {
                "id": 13058,
                "rootPlaceId": 1818,
                "name": "Classic: Crossroads",
                "description": "The classic ROBLOX level is back!",
                "sourceName": "Classic: Crossroads",
                "sourceDescription": "The classic ROBLOX level is back!",
                "creator": {
                    "id": 1,
                    "name": "Roblox",
                    "type": "User",
                    "isRNVAccount": false,
                    "hasVerifiedBadge": true
                },
                "price": null,
                "allowedGearGenres": [
                    "Ninja"
                ],
                "allowedGearCategories": [],
                "isGenreEnforced": true,
                "copyingAllowed": true,
                "playing": 21,
                "visits": 10809119,
                "maxPlayers": 8,
                "created": "2007-05-01T01:07:04.78Z",
                "updated": "2024-01-29T22:05:10.417Z",
                "studioAccessToApisAllowed": false,
                "createVipServersAllowed": false,
                "universeAvatarType": "MorphToR6",
                "genre": "Fighting",
                "genre_l1": "Action",
                "genre_l2": "Battlegrounds & Fighting",
                "isAllGenre": false,
                "isFavoritedByUser": false,
                "favoritedCount": 229776
            }
        ]
    }
    """
    universe_check = get_request_url(f"https://games.roblox.com/v1/games?universeIds={str(universe_id)}")
    if universe_check.ok:
        universe_json = universe_check.json()
        if "errors" in universe_json:
            error_n_print(f"Error in universe_json! [{universe_json}]")
            return False
        else:
            vvPrint(f"universe_json: [{universe_json}]")
            return universe_json["data"][0]
    return False


def get_group_info(group_id) -> dict:
    """
    Gets group/community information from group ID.

    Example JSON:
    {
        "data": [
            {
                "id": 7,
                "name": "Roblox",
                "description": "Official fan club of Roblox!",
                "owner": {
                    "id": 21557,
                    "type": "User"
                },
                "created": "2009-07-30T05:36:10.417Z",
                "hasVerifiedBadge": false
            }
        ]
    }
    """
    groupinfo_check = get_request_url(f"https://groups.roblox.com/v2/groups?groupIds={str(group_id)}")
    if groupinfo_check.ok:
        groupinfo_json = groupinfo_check.json()
        if "errors" in groupinfo_json:
            error_n_print(f"Error in groupinfo_json! [{groupinfo_json}]")
            return False
        else:
            vvPrint(f"groupinfo_json: [{groupinfo_json}]")
            return groupinfo_json["data"][0]
    return False


def find_group_places(group_id) -> list:
    """
    Finds group places from group ID.
    """
    vPrint(f"Searching group {str(group_id)}'s games...")
    group_places = []
    url = f"https://games.roblox.com/v2/groups/{str(group_id)}/games?accessFilter=2&limit=100&sortOrder=Asc"
    while True:
        groupplaces_check = get_request_url(url)
        if groupplaces_check.ok:
            groupplaces_json = groupplaces_check.json()
            if 'errors' in groupplaces_json:
                error_n_print(f"Error in groupplaces_json! [{groupplaces_json}]")
                return group_places

            vvPrint(f"groupplaces_json: [{groupplaces_json}]")

            for game in groupplaces_json['data']:
                root_place_id = game['rootPlace']['id']
                group_places.append(root_place_id)

            if groupplaces_json['nextPageCursor'] is None:
                vPrint("Found all games in group.")
                return group_places

            vPrint("Checking next page of games...")
            url = f"https://games.roblox.com/v2/groups/{str(group_id)}/games?accessFilter=2&limit=100&sortOrder=Asc&cursor={groupplaces_json['nextPageCursor']}"
        else:
            error_n_print(f"Error! [{groupplaces_check}]")
            return group_places


def get_user_info(user_id) -> dict:
    """
    Gets user information from user ID.

    Example JSON:
    {
        "description": "Welcome to the Roblox profile! This is where you can check out the newest items in the catalog, and get a jumpstart on exploring and building on our Imagination Platform. If you want news on updates to the Roblox platform, or great new experiences to play with friends, check out blog.roblox.com. Please note, this is an automated account. If you need to reach Roblox for any customer service needs find help at www.roblox.com/help",
        "created": "2006-02-27T21:06:40.3Z",
        "isBanned": false,
        "externalAppDisplayName": null,
        "hasVerifiedBadge": true,
        "id": 1,
        "name": "Roblox",
        "displayName": "Roblox"
    }
    """
    userinfo_check = get_request_url(f"https://users.roblox.com/v1/users/{str(user_id)}")
    if userinfo_check.ok:
        userinfo_json = userinfo_check.json()
        if "errors" in userinfo_json:
            error_n_print(f"Error in userinfo_json! [{userinfo_json}]")
            return False
        vvPrint(f"userinfo_json: [{userinfo_json}]")
        return userinfo_json
    return False


def find_user_places(user_id) -> list:
    """
    Finds user places from user ID.
    Loops through until final page is found.
    """
    vPrint(f"Searching user {str(user_id)}'s games...")
    user_places = []
    url = f"https://games.roblox.com/v2/users/{str(user_id)}/games?limit=50&sortOrder=Asc"
    while True:
        userplaces_check = get_request_url(url)
        if userplaces_check.ok:
            userplaces_json = userplaces_check.json()
            if 'errors' in userplaces_json:
                error_n_print(f"Error in userplaces_json! [{userplaces_json}]")
                return user_places

            vvPrint(f"userplaces_json: [{userplaces_json}]")
            for game in userplaces_json['data']:
                root_place_id = game['rootPlace']['id']
                user_places.append(root_place_id)

            if userplaces_json['nextPageCursor'] is None:
                vPrint("Found all games in user.")
                return user_places

            vPrint("Checking next page of games...")
            url = f"https://games.roblox.com/v2/users/{str(user_id)}/games?limit=50&sortOrder=Asc&cursor={userplaces_json['nextPageCursor']}"
        else:
            error_n_print(f"Error! [{userplaces_check}]")
            return user_places


def get_universe_votes(universe_id) -> dict:
    """
    Gets universe votes from universe ID.

    Example JSON:
    {
        "data": [
            {
                "id": 5988568657,
                "upVotes": 8922,
                "downVotes": 670
            }
        ]
    }
    """
    universevotes_check = get_request_url(f"https://games.roblox.com/v1/games/votes?universeIds={str(universe_id)}")
    if universevotes_check.ok:
        universevotes_json = universevotes_check.json()
        if "errors" in universevotes_json:
            error_n_print(f"Error in universevotes_json! [{universevotes_json}]")
            return False
        vvPrint(f"universevotes_json: [{universevotes_json}]")
        return universevotes_json["data"][0]
    return False


def check_user_inv_with_inventory_api(user_id=0, asset_id=0) -> bool:
    """
    Checks if user has an *ASSET* in their inventory.
    Results are not cached.

    DO NOT USE THIS TO CHECK FOR BADGES ABOVE 2124421088!
    See checkUserInvForBadge for info.
    """
    if user_id != 0 and user_id is not None and asset_id != 0:
        # inventory_api outputs just "true" or "false" in lowercase
        userasset_check = get_request_url(f"https://inventory.roblox.com/v1/users/{str(user_id)}/items/2/{str(asset_id)}/is-owned", cache_results=False)
        if userasset_check.ok:
            if userasset_check.text == "true":
                return True
            if userasset_check.text == "false":
                return False
    return None


def check_user_inv_for_badge(user_id=0, badge_id=0) -> bool:
    """
    Checks if user has a *BADGE* in their inventory.
    Results are not cached.

    Badge IDs and Asset IDs use different ID systems.

    Badges split off from assets in July 2018,
    the above function looks like it will work for
    every badge until you get to those newer badges.

    This function uses the Badges API, which
    will check the newer badges as intended.
    The only downside is that it's more rate
    limited than the inventory API.

    So, if the specifed badge ID is below 2124421087 (the first badge ID - 1),
    the function will call check_user_inv_with_inventory_api to utilise
    the better rate limit api.
    """
    if badge_id <= 2124421087:  # should be before the first badge id
        return check_user_inv_with_inventory_api(user_id=user_id, asset_id=badge_id)

    if user_id != 0 and user_id is not None and badge_id != 0:
        userbadge_check = get_request_url(f"https://badges.roblox.com/v1/users/{str(user_id)}/badges/awarded-dates?badgeIds={str(badge_id)}", cache_results=False)
        if userbadge_check.ok:
            userbadge_json = userbadge_check.json()
            if userbadge_json["data"] == []:
                return False
            return True
    return None


# https://stackoverflow.com/a/312464
def _chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def multicheck_user_inv_for_badges(user_id=0, badge_ids=[], retry_amount=2) -> list[bool]:
    """
    Checks multiple badges in user's inventory.
    Results are not cached.

    This only uses the badges API to check,
    as the inventory API does not have a method
    to multicheck assets.
    """
    badge_ids = list(set(badge_ids))  # dedupe list
    if user_id != 0 and user_id is not None and len(badge_ids) != 0:
        if len(badge_ids) > 100:
            combined_badge_dict = {}
            for b_chunk in _chunks(badge_ids, 100):
                combined_badge_dict = {**combined_badge_dict, **multicheck_user_inv_for_badges(user_id, b_chunk)}
            return combined_badge_dict

        badge_dict = {}
        for _ in range(retry_amount):
            userbadge_check = get_request_url(f"https://badges.roblox.com/v1/users/{str(user_id)}/badges/awarded-dates?badgeIds={','.join(badge_ids)}", cache_results=False)
            if userbadge_check.ok:
                userbadge_json = userbadge_check.json()
                if userbadge_json["data"] == []:
                    return {}

                for badge in userbadge_json["data"]:
                    badge_dict[badge["badgeId"]] = False
                    if str(badge["badgeId"]) in badge_ids:
                        badge_dict[badge["badgeId"]] = True
                return badge_dict
            time.sleep(3)
        return {}
    return None


def get_universe_badges_first_page(universe_id) -> dict:
    """
    Gets the first page of universe badges.
    If there are no badges in 'data', it returns false.
    Used to check if the universe contains any badges.

    Example JSON:
    {
        "previousPageCursor": null,
        "nextPageCursor": "{NEXTPAGECURSOR}",
        "data": [
            {
                "id": 2124422674,
                "name": "You visited!",
                "description": "Thanks for visiting!",
                "displayName": "You visited!",
                "displayDescription": "Thanks for visiting!",
                "enabled": true,
                "iconImageId": 2177787489,
                "displayIconImageId": 2177787489,
                "created": "2018-08-06T05:47:40.36+00:00",
                "updated": "2024-11-19T19:24:07.956+00:00",
                "statistics": {
                    "pastDayAwardedCount": 1,
                    "awardedCount": 8113,
                    "winRatePercentage": 1.0
                },
                "awardingUniverse": {
                    "id": 718992538,
                    "name": "Escape The Clown Obby",
                    "rootPlaceId": 2039280318
                }
            },
            {
                "id": 2124422675,
                "name": "YOU WON!",
                "description": "Congratulations, you made it all the way!",
                "displayName": "YOU WON!",
                "displayDescription": "Congratulations, you made it all the way!",
                "enabled": true,
                "iconImageId": 2177807506,
                "displayIconImageId": 2177807506,
                "created": "2018-08-06T05:54:17.323+00:00",
                "updated": "2024-11-19T19:24:07.957+00:00",
                "statistics": {
                    "pastDayAwardedCount": 1,
                    "awardedCount": 324,
                    "winRatePercentage": 1.0
                },
                "awardingUniverse": {
                    "id": 718992538,
                    "name": "Escape The Clown Obby",
                    "rootPlaceId": 2039280318
                }
            }
        ]
    }
    """
    universebadges_check = get_request_url(f"https://badges.roblox.com/v1/universes/{str(universe_id)}/badges")  # ?limit=10&sortOrder=Asc")
    if universebadges_check.ok:
        universebadges_json = universebadges_check.json()
        vvPrint(f"universebadges_json: [{universebadges_json}]")
        if universebadges_json["data"] == []:
            return False  # no badges
        return universebadges_json["data"]
    return None


def get_universe_from_place_id(place_id) -> dict:
    """
    Gets the universe ID from a place ID.

    Example JSON:
    {
        "universeId": 13058
    }
    """
    universeid_check = get_request_url(f"https://apis.roblox.com/universes/v1/places/{str(place_id)}/universe")
    if universeid_check.ok:
        universeid_json = universeid_check.json()
        vvPrint(f"universeid_json: [{universeid_json}]")
        return universeid_json["universeId"]
    return None


def get_user_from_token() -> dict:
    """
    Gets user ID from .ROBLOSECURITY token.
    Results are not cached.
    """
    usercheck = get_request_url("https://users.roblox.com/v1/users/authenticated", cache_results=False)
    if usercheck.ok:
        return usercheck.json()
    return None

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
