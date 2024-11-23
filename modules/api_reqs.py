# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/api_reqs.py
"""
Request handling for alcubierre.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import time
import random
import math
import requests

from modules import data_save
from modules.verbose_print import vPrint, vvPrint

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
        print("Warning: Ecomony API is limited to 1 request per minute!\nPlace playability info is unavailable!\nAdding your Roblox token is highly recommended!")


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
        return RESPONSE_CACHE[url]

    tries = 0
    vPrint(f"Requesting {url}...")
    for _ in range(retry_amount):
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
            print(f"Something happened when trying to get [{url}]!")
            print("Sleeping", sleep_time, "seconds...")
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
    {"TargetId":0,"ProductType":null,"AssetId":123456,"ProductId":0,"Name":"blackcatgoth"s Place","Description":"","AssetTypeId":9,"Creator":{"Id":52988,"Name":"blackcatgoth","CreatorType":"User","CreatorTargetId":52988,"HasVerifiedBadge":false},"IconImageAssetId":752403374,"Created":"2007-08-27T17:40:45.12Z","Updated":"2007-08-27T17:40:45.12Z","PriceInRobux":null,"PriceInTickets":null,"Sales":0,"IsNew":false,"IsForSale":false,"IsPublicDomain":false,"IsLimited":false,"IsLimitedUnique":false,"Remaining":null,"MinimumMembershipLevel":0,"ContentRatingTypeId":0,"SaleAvailabilityLocations":null,"SaleLocation":null,"CollectibleItemId":null,"CollectibleProductId":null,"CollectiblesItemDetails":null}
    """
    economy_check = get_request_url(f"https://economy.roblox.com/v2/assets/{str(asset_id)}/details", initial_wait_time=60)
    if economy_check.ok:
        economy_json = economy_check.json()
        if "errors" in economy_json:
            vPrint(f"Error in economy_json! [{economy_json}]")
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
    {"placeId": 20876709, "name": "[ Content Deleted ]", "description": "[ Content Deleted ]", "sourceName": "[ Content Deleted ]", "sourceDescription": "[ Content Deleted ]", "url": "https://www.roblox.com/games/20876709/Content-Deleted", "builder": "Chevsterr", "builderId": 6128452, "hasVerifiedBadge": False, "isPlayable": False, "reasonProhibited": "AssetUnapproved", "universeId": 19043203, "universeRootPlaceId": 20876709, "price": 0, "imageToken": "T_20876709_5455"}
    """
    if is_token_cookie_there():
        place_check = get_request_url(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={str(place_id)}")
        if place_check.ok:
            place_json = place_check.json()
            if "errors" in place_json:
                vPrint(f"Error in place_json! [{place_json}]")
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

    example JSON:
    {"id": 14427263, "name": "Juice Tycoon Money Player Badge", "description": "Go On My Juice Tycoon To Earn This!!!", "displayName": "Juice Tycoon Money Player Badge", "displayDescription": "Go On My Juice Tycoon To Earn This!!!", "enabled": True, "iconImageId": 14426818, "displayIconImageId": 14426818, "created": "2009-08-13T07:56:44.337-05:00", "updated": "2015-12-21T15:09:14.887-06:00", "statistics": {"pastDayAwardedCount": 0, "awardedCount": 1756, "winRatePercentage": 0.0}, "awardingUniverse": {"id": 685746, "name": "JUICE TYCOON!! YOU CAN EARN A BADGE HERE!!!!", "rootPlaceId": 4285089}}

    example error:
    {"errors": [{"code": 1, "message": "Badge is invalid or does not exist.", "userFacingMessage": "Something went wrong"}]}
    """
    badge_check = get_request_url(f"https://badges.roblox.com/v1/badges/{str(badge_id)}")
    if badge_check.ok:
        badge_json = badge_check.json()
        if "errors" in badge_json:
            vPrint(f"Error in badge_json! [{badge_json}]")
            return False

        vvPrint(f"badge_json: [{badge_json}]")
        return badge_json
    return False


def get_universe_info(universe_id) -> dict:
    """
    Gets universe information from universe ID.

    Example JSON:
    {"data":[{"id":13058,"rootPlaceId":1818,"name":"Classic: Crossroads","description":"The classic ROBLOX level is back!","sourceName":"Classic: Crossroads","sourceDescription":"The classic ROBLOX level is back!","creator":{"id":1,"name":"Roblox","type":"User","isRNVAccount":false,"hasVerifiedBadge":true},"price":null,"allowedGearGenres":["Ninja"],"allowedGearCategories":[],"isGenreEnforced":true,"copyingAllowed":true,"playing":21,"visits":10809119,"maxPlayers":8,"created":"2007-05-01T01:07:04.78Z","updated":"2024-01-29T22:05:10.417Z","studioAccessToApisAllowed":false,"createVipServersAllowed":false,"universeAvatarType":"MorphToR6","genre":"Fighting","genre_l1":"Action","genre_l2":"Battlegrounds & Fighting","isAllGenre":false,"isFavoritedByUser":false,"favoritedCount":229776}]}
    """
    universe_check = get_request_url(f"https://games.roblox.com/v1/games?universeIds={str(universe_id)}")
    if universe_check.ok:
        universe_json = universe_check.json()
        if "errors" in universe_json:
            vPrint(f"Error in universe_json! [{universe_json}]")
            return False
        else:
            vvPrint(f"universe_json: [{universe_json}]")
            return universe_json["data"][0]
    return False


def get_group_info(group_id) -> dict:
    """
    Gets group information from group ID.
    """
    groupinfo_check = get_request_url(f"https://groups.roblox.com/v2/groups?groupIds={str(group_id)}")
    if groupinfo_check.ok:
        groupinfo_json = groupinfo_check.json()
        if "errors" in groupinfo_json:
            vPrint(f"Error in groupinfo_json! [{groupinfo_json}]")
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
                vPrint(f"Error in groupplaces_json! [{groupplaces_json}]")
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
            print(f"Error! [{groupplaces_check}]")
            return group_places


def get_user_info(user_id) -> dict:
    """
    Gets user information from user ID.
    """
    userinfo_check = get_request_url(f"https://users.roblox.com/v1/users/{str(user_id)}")
    if userinfo_check.ok:
        userinfo_json = userinfo_check.json()
        if "errors" in userinfo_json:
            vPrint(f"Error in userinfo_json! [{userinfo_json}]")
            return False

        vvPrint(f"userinfo_json: [{userinfo_json}]")
        return userinfo_json
    return False


def find_user_places(user_id) -> list:
    """
    Finds user places from user ID.
    """
    vPrint(f"Searching user {str(user_id)}'s games...")
    user_places = []
    url = f"https://games.roblox.com/v2/users/{str(user_id)}/games?limit=50&sortOrder=Asc"
    while True:
        userplaces_check = get_request_url(url)
        if userplaces_check.ok:
            userplaces_json = userplaces_check.json()
            if 'errors' in userplaces_json:
                vPrint(f"Error in userplaces_json! [{userplaces_json}]")
                return user_places

            vvPrint(f"userPlaces_json: [{userplaces_json}]")
            for game in userplaces_json['data']:
                root_place_id = game['rootPlace']['id']
                user_places.append(root_place_id)

            if userplaces_json['nextPageCursor'] is None:
                vPrint("Found all games in user.")
                return user_places

            vPrint("Checking next page of games...")
            url = f"https://games.roblox.com/v2/users/{str(user_id)}/games?limit=50&sortOrder=Asc&cursor={userplaces_json['nextPageCursor']}"
        else:
            print(f"Error! [{userplaces_check}]")
            return user_places


def get_universe_votes(universe_id) -> dict:
    """
    Gets universe votes from universe ID.

    Example JSON:
    {"data":[{"id":5988568657,"upVotes":8922,"downVotes":670}]}
    """
    universevotes_check = get_request_url(f"https://games.roblox.com/v1/games/votes?universeIds={str(universe_id)}")
    if universevotes_check.ok:
        universevotes_json = universevotes_check.json()
        if "errors" in universevotes_json:
            vPrint(f"Error in universevotes_json! [{universevotes_json}]")
            return False

        vvPrint(f"universevotes_json: [{universevotes_json}]")
        return universevotes_json["data"][0]
    return False


def check_user_inv_for_asset(user_id=0, asset_id=0) -> bool:
    """
    Checks if user has an *ASSET* in their inventory.

    DO NOT USE THIS TO CHECK FOR BADGES! (Specifically, any new badges)
    Technically deprecated, might become useful in the future.
    See checkUserInvForBadge for info.

    (TODO: find last asset-badge id, create hybrid function using both apis)
    """
    if user_id != 0 and user_id is not None and asset_id != 0:
        # inventory_api outputs just "true" or "false" in lowercase
        userasset_check = get_request_url(f"https://inventory.roblox.com/v1/users/{str(user_id)}/items/2/{str(asset_id)}/is-owned",cache_results=False)
        if userasset_check.ok:
            if userasset_check.text == "true":
                return True
            if userasset_check.text == "false":
                return False
    return None


def check_user_inv_for_badge(user_id=0, badge_id=0) -> bool:
    """
    Checks if user has a *BADGE* in their inventory.

    Badge IDs and Asset IDs use different ID systems.

    Badges split off from assets in July 2018,
    using the above function looks like it will work for
    every badge until you get to those newer badges.

    This function uses the correct API to check for badges.
    Only downside is that it's more rate limited than the inventory API.
    """
    if user_id != 0 and user_id is not None and badge_id != 0:
        userbadge_check = get_request_url(f"https://badges.roblox.com/v1/users/{str(user_id)}/badges/awarded-dates?badgeIds={str(badge_id)}", cache_results=False)
        if userbadge_check.ok:
            userbadge_json = userbadge_check.json()
            if userbadge_json["data"] == []:
                return False
            return True
    return None


def check_universe_for_any_badges(universe_id) -> dict:
    """
    Checks if the universe contains any badges.
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
    {"universeId":13058}
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
