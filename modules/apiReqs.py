import time, random, math, requests
#from . import dataSave

from modules.verbosePrint import vPrint

# temporary response cache
# TODO: create optional argument permCache as a file (and allow disabling caches)
tempRespCache = {"economy":{},"badges":{},"places":{},"universes":{}}

requestSession = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=5)
requestSession.mount("https://", adapter)
requestSession.mount("http://", adapter)

def init(user_agent=None,rbx_token=None):
    if not user_agent == None:
        requestSession.headers["User-Agent"] = str(user_agent)
    if not rbx_token == None:
        requestSession.cookies[".ROBLOSECURITY"] = str(rbx_token)
    else:
        print("Warning: Ecomony API is limited to 1 request per minute!")
        print("Warning! Place playability info is unavailable!")
        print("Adding your Roblox token is highly recommended!")
    #requestSession.headers["Referer"] = "https://www.roblox.com"

def isTokenCookieThere():
    return ".ROBLOSECURITY" in requestSession.cookies

def getRequestURL(url, retryAmount=8, acceptForbidden=False, initialWaitTime=None):
    tries = 0
    vPrint(f"Requesting {url}...")
    for _ in range(retryAmount):
        tries += 1
        try:
            response: requests.Response = requestSession.get(url)
            vPrint(response)
            if response.status_code == 200:
                return response
            if response.status_code == 302: # Found
                return response
            if acceptForbidden:
                if response.status_code == 403: # Forbidden
                    return response
            vPrint(response.status_code)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            vPrint("Timed out!")
            vPrint(f"Request failed: {e}")
        except requests.exceptions.TooManyRedirects:
            vPrint("Too many redirects!")
            vPrint(f"Request failed: {e}")
            return False
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                vPrint("Too many requests!")
            if response.status_code == 404:
                return response
            elif response.status_code == 403:
                vPrint("Token Validation Failed. Re-validating...")
                validate_CSRF()
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

def validate_CSRF():
    """
    Takes X-CSRF-Token from logout auth URL.
    """
    req = requests.post(url="https://auth.roblox.com/v2/logout")
    return req.headers["X-CSRF-Token"]

# {"TargetId":0,"ProductType":null,"AssetId":123456,"ProductId":0,"Name":"blackcatgoth"s Place","Description":"","AssetTypeId":9,"Creator":{"Id":52988,"Name":"blackcatgoth","CreatorType":"User","CreatorTargetId":52988,"HasVerifiedBadge":false},"IconImageAssetId":752403374,"Created":"2007-08-27T17:40:45.12Z","Updated":"2007-08-27T17:40:45.12Z","PriceInRobux":null,"PriceInTickets":null,"Sales":0,"IsNew":false,"IsForSale":false,"IsPublicDomain":false,"IsLimited":false,"IsLimitedUnique":false,"Remaining":null,"MinimumMembershipLevel":0,"ContentRatingTypeId":0,"SaleAvailabilityLocations":null,"SaleLocation":null,"CollectibleItemId":null,"CollectibleProductId":null,"CollectiblesItemDetails":null}
def getEconomyInfo(assetId,actLikePlaceDetailsAPI=False):
    economy_json = None

    if assetId in tempRespCache["places"]:
        economy_json = tempRespCache["places"][assetId]
        return economy_json

    economy_check = getRequestURL(f"https://economy.roblox.com/v2/assets/{str(assetId)}/details",initialWaitTime=60)
    if economy_check.ok:
        economy_json = economy_check.json()
        if "errors" in economy_json:
            vPrint(f"Error in economy_json! [{economy_json}]")
            return False
        else:
            vPrint(f"economy_json: [{economy_json}]")
            tempRespCache["economy"][assetId] = economy_json
            if actLikePlaceDetailsAPI:
                return {k.lower(): v for k, v in economy_json.items()}
            return economy_json

# {"placeId": 20876709, "name": "[ Content Deleted ]", "description": "[ Content Deleted ]", "sourceName": "[ Content Deleted ]", "sourceDescription": "[ Content Deleted ]", "url": "https://www.roblox.com/games/20876709/Content-Deleted", "builder": "Chevsterr", "builderId": 6128452, "hasVerifiedBadge": False, "isPlayable": False, "reasonProhibited": "AssetUnapproved", "universeId": 19043203, "universeRootPlaceId": 20876709, "price": 0, "imageToken": "T_20876709_5455"}
def getPlaceInfo(placeId,noAlternative=False):
    if isTokenCookieThere():
        place_json = None

        if placeId in tempRespCache["places"]:
            place_json = tempRespCache["places"][placeId]
            return place_check

        place_check = getRequestURL(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={str(placeId)}")
        if place_check.ok:
            place_json = place_check.json()
            if "errors" in place_json:
                vPrint(f"Error in place_json! [{place_json}]")
                return False
            else:
                #vPrint(f"place_json: [{place_json}]")
                tempRespCache["places"][placeId] = place_json[0]
                return place_json[0]

        # except ConnectionError:
        #     print("Connection Error! Attempting to retry...")
        #     time.sleep(10)
        #     validate()
        #attempts += 1
        else:
            return False
    elif noAlternative == False:
        vPrint("multiget-place-details is unusable, but alternative is allowed.")
        vPrint("Using economy API with compatability-esque keys...")
        return getEconomyInfo(placeId,actLikePlaceDetailsAPI=True)
    else:
        vPrint("multiget-place-details is unusable; cannot use economy api for this. Returning false.")
        return False

def getBadgeInfo(badgeId):
    if badgeId in tempRespCache["badges"]:
        return tempRespCache["badges"][badgeId]

    # example of badge_api success
    # {"id": 14427263, "name": "Juice Tycoon Money Player Badge", "description": "Go On My Juice Tycoon To Earn This!!!", "displayName": "Juice Tycoon Money Player Badge", "displayDescription": "Go On My Juice Tycoon To Earn This!!!", "enabled": True, "iconImageId": 14426818, "displayIconImageId": 14426818, "created": "2009-08-13T07:56:44.337-05:00", "updated": "2015-12-21T15:09:14.887-06:00", "statistics": {"pastDayAwardedCount": 0, "awardedCount": 1756, "winRatePercentage": 0.0}, "awardingUniverse": {"id": 685746, "name": "JUICE TYCOON!! YOU CAN EARN A BADGE HERE!!!!", "rootPlaceId": 4285089}}
    # example of badge_api error
    # {"errors": [{"code": 1, "message": "Badge is invalid or does not exist.", "userFacingMessage": "Something went wrong"}]}
    badge_check = getRequestURL(f"https://badges.roblox.com/v1/badges/{str(badgeId)}")

    #print(badge_check.text)
    if badge_check.ok:
        badge_json = badge_check.json()
        if "errors" in badge_json:
            vPrint(f"Error in badge_json! [{badge_json}]")
            return False
        else:
            #vPrint(f"badge_json: [{badge_json}]")
            tempRespCache["badges"][badgeId] = badge_json
            return badge_json
    else:
        return False

# {"data":[{"id":13058,"rootPlaceId":1818,"name":"Classic: Crossroads","description":"The classic ROBLOX level is back!","sourceName":"Classic: Crossroads","sourceDescription":"The classic ROBLOX level is back!","creator":{"id":1,"name":"Roblox","type":"User","isRNVAccount":false,"hasVerifiedBadge":true},"price":null,"allowedGearGenres":["Ninja"],"allowedGearCategories":[],"isGenreEnforced":true,"copyingAllowed":true,"playing":21,"visits":10809119,"maxPlayers":8,"created":"2007-05-01T01:07:04.78Z","updated":"2024-01-29T22:05:10.417Z","studioAccessToApisAllowed":false,"createVipServersAllowed":false,"universeAvatarType":"MorphToR6","genre":"Fighting","genre_l1":"Action","genre_l2":"Battlegrounds & Fighting","isAllGenre":false,"isFavoritedByUser":false,"favoritedCount":229776}]}
def getUniverseInfo(universeId):
    # ah, i forgot about the whole "id overlap" thing...
    if universeId in tempRespCache["universes"]:
        return tempRespCache["universes"][universeId]
    
    universe_check = getRequestURL(f"https://games.roblox.com/v1/games?universeIds={str(universeId)}")

    #print(badge_check.text)
    if universe_check.ok:
        universe_json = universe_check.json()
        if "errors" in universe_json:
            vPrint(f"Error in universe_json! [{universe_json}]")
            return False
        else:
            #vPrint(f"universe_json: [{universe_json}]")
            tempRespCache["universes"][universeId] = universe_json
            return universe_json
    else:
        return False

def checkUserInvForAsset(userId=0, assetId=0):
    # check if user has badge
    if not userId == 0 and not assetId == 0:
        # inventory_api should only output "true" or "false"; all lowercase
        user_check = getRequestURL(f"https://inventory.roblox.com/v1/users/{str(userId)}/items/2/{str(assetId)}/is-owned")

        if user_check.text == "true":
            return True
        elif user_check.text == "false":
            return False
        else:
            return None
    else:
        return None

def checkUniverseForAnyBadges(universeId):
    universeBadgesCheck = getRequestURL(f"https://badges.roblox.com/v1/universes/{str(universeId)}/badges")#?limit=10&sortOrder=Asc")
    #(badge_api + "universes/" + str(universeId) + "/badges?limit=10&sortOrder=Asc")
    if universeBadgesCheck.ok:
        universeBadges_json = universeBadgesCheck.json()
        vPrint(f"universeBadges_json: [{universeBadges_json}]")
        if universeBadges_json["data"] == []: # no badges
            return False
        else:
            return universeBadges_json["data"]

# {"universeId":13058}
def getUniverseFromPlaceId(placeId):
    universeIdCheck = getRequestURL(f"https://apis.roblox.com/universes/v1/places/{str(placeId)}/universe")
    if universeIdCheck.ok:
        universe_json = universeIdCheck.json()
        vPrint(f"universe_json: [{universe_json}]")
        #print(universe_json)
        return universe_json["universeId"]
    return None

def getUserFromToken():
    userCheck = getRequestURL("https://users.roblox.com/v1/users/authenticated")
    if userCheck.ok:
        return userCheck.json()