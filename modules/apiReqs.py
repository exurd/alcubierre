# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/apiReqs.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

import time, random, math, requests
from . import dataSave

from modules.verbosePrint import vPrint

# temporary response cache
respCache = {}

usingPermCache = False
def _getPermCache():
    global usingPermCache
    global respCache
    usingPermCache = True

    permRespCache = dataSave.load_data("responseCache.pickle",asDict=True)
    if permRespCache == {}: return
    respCache = permRespCache

def _saveToPermCache(url,response,cacheResults=True) -> requests.Response:
    response.request.headers = None # stops cookies from being saved into the pickle
    if cacheResults and usingPermCache:
        global respCache
        respCache[url] = response
        dataSave.save_data(respCache,"responseCache.pickle")
    return response

requestSession = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=5)
requestSession.mount("https://", adapter)
requestSession.mount("http://", adapter)

def init(user_agent=None,rbx_token=None):
    if not user_agent == None: requestSession.headers["User-Agent"] = str(user_agent)

    if not rbx_token == None: requestSession.cookies[".ROBLOSECURITY"] = str(rbx_token)
    else: print("Warning: Ecomony API is limited to 1 request per minute!\nPlace playability info is unavailable!\nAdding your Roblox token is highly recommended!")

def isTokenCookieThere() -> bool: return ".ROBLOSECURITY" in requestSession.cookies

def getRequestURL(url,retryAmount=8,acceptForbidden=False,acceptNotFound=True,initialWaitTime=None,cacheResults=True) -> requests.Response:
    if type(url) != str: vPrint("getRequestURL: url was not string type, sending None"); return None
    if cacheResults and url in respCache: return respCache[url]
    tries = 0
    vPrint(f"Requesting {url}...")
    for _ in range(retryAmount):
        tries += 1
        try:
            response = requestSession.get(url)
            vPrint(f"Response Status Code: {response.status_code}")
            sc = response.status_code
            if sc == 200 or sc == 302: return _saveToPermCache(url,response,cacheResults) # OK, Found
            if acceptForbidden and sc == 403: return _saveToPermCache(url,response,cacheResults) # Forbidden (if acceptForbidden)
            if acceptNotFound and sc == 404: return _saveToPermCache(url,response,cacheResults) # Not Found (if acceptNotFound)
            if sc == 410: return _saveToPermCache(url,response,cacheResults) # Gone
            response.raise_for_status()
        except requests.exceptions.Timeout:
            vPrint("Timed out!")
            vPrint(f"Request failed: {e}")
        except requests.exceptions.TooManyRedirects:
            vPrint("Too many redirects!")
            vPrint(f"Request failed: {e}")
            return False
        except requests.exceptions.HTTPError as e:
            if sc == 403 or sc == 419: # Forbidden (Roblox sends 403 for some requests that need a CSRF token), Page Expired
                vPrint("Token Validation Failed. Re-validating...")
                validate_CSRF()
            elif sc == 400: return False # Bad Request
            elif sc == 429: # Too Many Requests
                vPrint("Too many requests!")
        except requests.exceptions.RequestException as e:
            vPrint(f"Request failed: {e}")
            return False
        if tries < retryAmount:
            sleep_time = random.randint(
                math.floor(2 ** (tries - 0.5)),
                math.floor(2 ** tries)
                )
            if initialWaitTime != None:
                sleep_time = int(initialWaitTime)
                initialWaitTime = None
            print(f"Something happened when trying to get [{url}]!")
            print("Sleeping", sleep_time, "seconds...")
            time.sleep(sleep_time)
    return False

def validate_CSRF() -> str:
    """
    Gets X-CSRF-Token for Roblox.
    """
    req = requests.post(url="https://auth.roblox.com/v2/logout")
    return req.headers["X-CSRF-Token"]

# {"TargetId":0,"ProductType":null,"AssetId":123456,"ProductId":0,"Name":"blackcatgoth"s Place","Description":"","AssetTypeId":9,"Creator":{"Id":52988,"Name":"blackcatgoth","CreatorType":"User","CreatorTargetId":52988,"HasVerifiedBadge":false},"IconImageAssetId":752403374,"Created":"2007-08-27T17:40:45.12Z","Updated":"2007-08-27T17:40:45.12Z","PriceInRobux":null,"PriceInTickets":null,"Sales":0,"IsNew":false,"IsForSale":false,"IsPublicDomain":false,"IsLimited":false,"IsLimitedUnique":false,"Remaining":null,"MinimumMembershipLevel":0,"ContentRatingTypeId":0,"SaleAvailabilityLocations":null,"SaleLocation":null,"CollectibleItemId":null,"CollectibleProductId":null,"CollectiblesItemDetails":null}
def getEconomyInfo(assetId,actLikePlaceDetailsAPI=False) -> dict:
    economy_check = getRequestURL(f"https://economy.roblox.com/v2/assets/{str(assetId)}/details",initialWaitTime=60)
    if economy_check.ok:
        economy_json = economy_check.json()
        if "errors" in economy_json:
            vPrint(f"Error in economy_json! [{economy_json}]")
            return False
        vPrint(f"economy_json: [{economy_json}]")
        if actLikePlaceDetailsAPI: return {k.lower(): v for k, v in economy_json.items()}
        return economy_json
    return False

# {"placeId": 20876709, "name": "[ Content Deleted ]", "description": "[ Content Deleted ]", "sourceName": "[ Content Deleted ]", "sourceDescription": "[ Content Deleted ]", "url": "https://www.roblox.com/games/20876709/Content-Deleted", "builder": "Chevsterr", "builderId": 6128452, "hasVerifiedBadge": False, "isPlayable": False, "reasonProhibited": "AssetUnapproved", "universeId": 19043203, "universeRootPlaceId": 20876709, "price": 0, "imageToken": "T_20876709_5455"}
def getPlaceInfo(placeId,noAlternative=False) -> dict:
    if isTokenCookieThere():
        place_check = getRequestURL(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={str(placeId)}")
        if place_check.ok:
            place_json = place_check.json()
            if "errors" in place_json:
                vPrint(f"Error in place_json! [{place_json}]")
                return False
            vPrint(f"place_json: [{place_json}]")
            return place_json[0]
        return False
    elif noAlternative == False:
        vPrint("multiget-place-details is unusable, but alternative is allowed.")
        vPrint("Using economy API with compatability-esque keys...")
        return getEconomyInfo(placeId,actLikePlaceDetailsAPI=True)
    else:
        vPrint("multiget-place-details is unusable; cannot use economy api for this. Returning false.")
        return False

# example of badge_api success
# {"id": 14427263, "name": "Juice Tycoon Money Player Badge", "description": "Go On My Juice Tycoon To Earn This!!!", "displayName": "Juice Tycoon Money Player Badge", "displayDescription": "Go On My Juice Tycoon To Earn This!!!", "enabled": True, "iconImageId": 14426818, "displayIconImageId": 14426818, "created": "2009-08-13T07:56:44.337-05:00", "updated": "2015-12-21T15:09:14.887-06:00", "statistics": {"pastDayAwardedCount": 0, "awardedCount": 1756, "winRatePercentage": 0.0}, "awardingUniverse": {"id": 685746, "name": "JUICE TYCOON!! YOU CAN EARN A BADGE HERE!!!!", "rootPlaceId": 4285089}}
# example of badge_api error
# {"errors": [{"code": 1, "message": "Badge is invalid or does not exist.", "userFacingMessage": "Something went wrong"}]}
def getBadgeInfo(badgeId) -> dict:
    badge_check = getRequestURL(f"https://badges.roblox.com/v1/badges/{str(badgeId)}")
    if badge_check.ok:
        badge_json = badge_check.json()
        if "errors" in badge_json:
            vPrint(f"Error in badge_json! [{badge_json}]")
            return False
        else:
            vPrint(f"badge_json: [{badge_json}]")
            return badge_json
    return False

# {"data":[{"id":13058,"rootPlaceId":1818,"name":"Classic: Crossroads","description":"The classic ROBLOX level is back!","sourceName":"Classic: Crossroads","sourceDescription":"The classic ROBLOX level is back!","creator":{"id":1,"name":"Roblox","type":"User","isRNVAccount":false,"hasVerifiedBadge":true},"price":null,"allowedGearGenres":["Ninja"],"allowedGearCategories":[],"isGenreEnforced":true,"copyingAllowed":true,"playing":21,"visits":10809119,"maxPlayers":8,"created":"2007-05-01T01:07:04.78Z","updated":"2024-01-29T22:05:10.417Z","studioAccessToApisAllowed":false,"createVipServersAllowed":false,"universeAvatarType":"MorphToR6","genre":"Fighting","genre_l1":"Action","genre_l2":"Battlegrounds & Fighting","isAllGenre":false,"isFavoritedByUser":false,"favoritedCount":229776}]}
def getUniverseInfo(universeId) -> dict:
    universe_check = getRequestURL(f"https://games.roblox.com/v1/games?universeIds={str(universeId)}")
    if universe_check.ok:
        universe_json = universe_check.json()
        if "errors" in universe_json:
            vPrint(f"Error in universe_json! [{universe_json}]")
            return False
        else:
            vPrint(f"universe_json: [{universe_json}]")
            return universe_json["data"][0]
    return False

# {"data":[{"id":5988568657,"upVotes":8922,"downVotes":670}]}
def getUniverseVotes(universeId) -> dict:
    universeVotes_check = getRequestURL(f"https://games.roblox.com/v1/games/votes?universeIds={str(universeId)}")
    if universeVotes_check.ok:
        universeVotes_json = universeVotes_check.json()
        if "errors" in universeVotes_json:
            vPrint(f"Error in universeVotes_json! [{universeVotes_json}]")
            return False
        vPrint(f"universeVotes_json: [{universeVotes_json}]")
        return universeVotes_json["data"][0]
    return False

def checkUserInvForAsset(userId=0,assetId=0) -> bool:
    """
    DO NOT USE THIS TO CHECK FOR BADGES!
    (Specifically, any new badges)
    Technically deprecated, might become useful in the future
    (TODO: find last asset-badge id, create hybrid function using both apis)
    See checkUserInvForBadge for info.
    """
    if not userId == 0 and not userId == None and not assetId == 0:
        # inventory_api outputs just "true" or "false" in lowercase
        userAsset_check = getRequestURL(f"https://inventory.roblox.com/v1/users/{str(userId)}/items/2/{str(assetId)}/is-owned",cacheResults=False)
        if userAsset_check.ok:
            if userAsset_check.text == "true": return True
            elif userAsset_check.text == "false": return False
    return None

def checkUserInvForBadge(userId=0,badgeId=0) -> bool:
    """
    Badge IDs and Asset IDs use different ID systems.

    Badges split off from assets in July 2018,
    using the above function looks like it will work for
    every badge until you get to those newer badges.

    This function uses the correct API to check for badges.
    Only downside is that it's more rate limited than the inventory API.
    """
    if not userId == 0 and not userId == None and not badgeId == 0:
        userBadge_check = getRequestURL(f"https://badges.roblox.com/v1/users/{str(userId)}/badges/awarded-dates?badgeIds={str(badgeId)}",cacheResults=False)
        if userBadge_check.ok:
            userBadge_json = userBadge_check.json()
            if userBadge_json["data"] == []: return False
            else: return True
    return None

def checkUniverseForAnyBadges(universeId) -> dict:
    universeBadgesCheck = getRequestURL(f"https://badges.roblox.com/v1/universes/{str(universeId)}/badges")#?limit=10&sortOrder=Asc")
    if universeBadgesCheck.ok:
        universeBadges_json = universeBadgesCheck.json()
        vPrint(f"universeBadges_json: [{universeBadges_json}]")
        if universeBadges_json["data"] == []: return False # no badges
        else:
            vPrint(f"universeBadges_json: [{universeBadges_json}]"); return universeBadges_json["data"]
    return None

# {"universeId":13058}
def getUniverseFromPlaceId(placeId) -> dict:
    universeIdCheck = getRequestURL(f"https://apis.roblox.com/universes/v1/places/{str(placeId)}/universe")
    if universeIdCheck.ok:
        universeId_json = universeIdCheck.json()
        vPrint(f"universeId_json: [{universeId_json}]")
        return universeId_json["universeId"]
    return None

def getUserFromToken() -> dict:
    userCheck = getRequestURL("https://users.roblox.com/v1/users/authenticated",cacheResults=False)
    if userCheck.ok: return userCheck.json()
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