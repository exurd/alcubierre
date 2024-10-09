import re
from enum import Enum

from . import apiReqs
from .verbosePrint import vPrint

place_patterns = [
    r"roblox\.com/games/(\d+)",
    r"place\?id=(\d+)"
]
badge_patterns = [
    r"roblox\.com/badges/(\d+)",
    r"item\?id=(\d+)"
]

class rbxType(Enum):
    UNKNOWN = 0
    BADGE = 1
    PLACE = 2
    UNIVERSE = 3

class rbxReason(Enum):
    """
    Positive numbers 'good', negative numbers 'bad'.
    """
    badgeCollected = 4
    timeUp = 3
    processClosed = 2
    processOpened = 1
    alreadyCollected = -1
    notEnabled = -2
    noBadgesInUniverse = -3
    alreadyPlayed = -4
    notPlayable = -5
    notEnoughPlayersAwarded = -6
    noUniverse = -7

class rbxInstance:
    def __init__(self, id=None, type=None):
        self.id = id
        self.type = type
        self.info = None # no info yet as it was just created

    def __str__(self):
        return f"rbxInstance [id: {self.id}, type: {self.type}]"
    
    def getInfoFromType(self):
        vPrint(f"Getting info for {self.id} with type {self.type}")
        if self.type == rbxType.BADGE:
            badgeInfo = apiReqs.getBadgeInfo(self.id)
            vPrint(f"badgeInfo: {badgeInfo}")
            if badgeInfo != False:
                self.info = badgeInfo
                return badgeInfo
        if self.type == rbxType.PLACE:
            placeInfo = apiReqs.getPlaceInfo(self.id)
            vPrint(f"placeInfo: {placeInfo}")
            if placeInfo != False:
                self.info = placeInfo
                return placeInfo
        if self.type == rbxType.UNIVERSE:
            universeInfo = apiReqs.getUniverseInfo(self.id)
            vPrint(f"universeInfo: {universeInfo}")
            if universeInfo != False:
                self.info = universeInfo
                return universeInfo
    
    def stringIdThingy(self,string:str):
        vPrint("Detecting type from string...")
        id = None
        idType = None
        if "badge::" in string:
            #print(string)
            id = string.replace("badge::","")
            idType = rbxType.BADGE
        if "place::" in string:
            #print(string)
            id = string.replace("place::","")
            idType = rbxType.PLACE
        if "universe::" in string:
            id = string.replace("universe::","")
            idType = rbxType.UNIVERSE
        
        for pattern in place_patterns:
            if id != None and idType != None:   break
            match = re.search(pattern, string)
            if match:
                id = match.group(1)
                idType = rbxType.PLACE
        
        for pattern in badge_patterns:
            if id != None and idType != None:   break
            match = re.search(pattern, string)
            if match:
                id = match.group(1)
                idType = rbxType.BADGE
        
        # check if string is a number (id)
        if id == None and idType == None:
            vPrint("Last ditch effort, checking if string is just an integer...")
            try:
                checkInt = int(string)
                vPrint("String is an id, setting type to rbxType.UNKNOWN")
                id = string
                idType = rbxType.UNKNOWN
            except ValueError:
                vPrint("...welp, it's not an integer.")

        self.id = id
        self.type = idType
        vPrint(self)
    
    def detectTypeFromId(self,ignore=[]) -> rbxType:
        id = self.id
        vPrint(f"Attempt to detect type from {id}")

        vPrint("Badge?")
        if not rbxType.BADGE in ignore:
            badgeInfo = apiReqs.getBadgeInfo(id)
            if badgeInfo != False:
                self.type = rbxType.BADGE
                return rbxType.BADGE

        vPrint("Place?")
        if not rbxType.PLACE in ignore:
            economyInfo = apiReqs.getEconomyInfo(id)
            if economyInfo != False:
                # economy api is broad; check if the asset type is 9 (place)
                print(economyInfo)
                if economyInfo["AssetTypeId"] == 9:
                    self.type = rbxType.PLACE
                    return rbxType.PLACE
        
        # universes use a seperate id system from places and badges, so one could be confused for the other.
        # when making a text file with just the ids *please* use {type}::{id} to specify what type each line is!
        # otherwise, most if not all universe ids will get misjudged as a badge/place id.
        vPrint("Universe?")
        if not rbxType.UNIVERSE in ignore:
            universeInfo = apiReqs.getUniverseInfo(id)
            if universeInfo != False:
                self.type = rbxType.UNIVERSE
                return rbxType.UNIVERSE

        # tried everything? set to None and give up on this one
        vPrint("Mineral...? *shrug*")
        vPrint("Tried every type. Setting self.type to None.")
        self.type = None
        return None