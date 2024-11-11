# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/rbxTypes.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

import re
from enum import Enum

from . import apiReqs
from .verbosePrint import vPrint

def checkIfStringIsInteger(string:str):
    vPrint(f"Checking if string {string} is an integer...")
    try:
        checkInt = int(string)
        vPrint("String is an integer.")
        return checkInt
    except ValueError:
        vPrint("String is not an integer.")
        return None

class rbxType(Enum):
    """
    Positive: singular item
    Negative: multiple items
    """
    def __str__(self): return self.name
    USER = -2
    GROUP = -1
    UNKNOWN = 0
    BADGE = 1
    PLACE = 2
    UNIVERSE = 3

TYPE_PATTERNS = {
    rbxType.PLACE: [
        re.compile(r"roblox\.com/games/(\d+)", re.IGNORECASE),
        re.compile(r"place\?id=(\d+)", re.IGNORECASE),
        re.compile(r"roblox\.com/Place\.aspx\?ID=(\d+)", re.IGNORECASE),
        re.compile(r"roblox\.com/PlaceItem\.aspx\?id=(\d+)", re.IGNORECASE)
    ],
    rbxType.BADGE: [
        re.compile(r"roblox\.com/badges/(\d+)", re.IGNORECASE),
        re.compile(r"item\?id=(\d+)", re.IGNORECASE)
    ],
    rbxType.GROUP: [
        re.compile(r"roblox\.com/groups/(\d+)", re.IGNORECASE),
    ],
    rbxType.USER: [
        re.compile(r"roblox\.com/users/(\d+)", re.IGNORECASE),
        re.compile(r"roblox\.com/User\.aspx\?ID=(\d+)", re.IGNORECASE)
    ]
}

TYPE_STRINGS = {
    rbxType.PLACE: [
        "place::", "places::", "p::",
        "game::", "games::"
    ],
    rbxType.BADGE: [
        "badge::", "badges::", "b::"
    ],
    rbxType.UNIVERSE: [
        "universe::", "universes::", "u::"
    ],
    rbxType.GROUP: [
        "group::", "groups::", "g::"
    ],
    rbxType.USER: [
        "user::", "users::", "u::"
    ]
}

def checkTypeStrings(string:str):
    for RBX_TYPE, COLON_STRINGS in TYPE_STRINGS.items():
        vPrint(f"Checking '::' strings for type: {RBX_TYPE}")
        for colonString in COLON_STRINGS:
            vPrint(f"'::' string: {colonString}")
            if colonString in string:
                id = string.replace(colonString,"")
                idType = RBX_TYPE
                return id, idType
    return None, None

def checkRegExStrings(string:str):
    for RBX_TYPE, PATTERNS in TYPE_PATTERNS.items():
        vPrint(f"Checking patterns for type: {RBX_TYPE}")
        for pattern in PATTERNS:
            vPrint(f"Pattern: {pattern}")
            match = pattern.search(string)
            if match:
                id = match.group(1)
                idType = RBX_TYPE
                return id, idType
    return None, None

class rbxReason(Enum):
    """
    Positive: 'good' outcome
    Negative: 'bad' outcome
    """
    def __str__(self): return self.name
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
    badVoteRatio = -8

class rbxInstance:
    def __init__(self, id=None, type=None):
        self.id = id
        self.type = type
        self.info = None # no info yet as it was just created

    def __str__(self): return f"rbxInstance [id: {self.id}, type: {self.type}]"
    
    def getInfoFromType(self):
        vPrint(f"Getting info for {self.id} with type {self.type}")
        info = False
        if self.type == rbxType.BADGE:
            info = apiReqs.getBadgeInfo(self.id)
        if self.type == rbxType.PLACE:
            info = apiReqs.getPlaceInfo(self.id)
        if self.type == rbxType.UNIVERSE:
            info = apiReqs.getUniverseInfo(self.id)
        if self.type == rbxType.GROUP:
            info = apiReqs.getGroupInfo(self.id)
        if self.type == rbxType.USER:
            info = apiReqs.getUserInfo(self.id)
        
        if info != False:
            self.info = info
            return info
    
    def stringIdThingy(self,string:str):
        if type(string) != str: self.type = None; return None
        vPrint("Detecting type from string...")
        id = None
        idType = None

        if "::" in string:
            id, idType = checkTypeStrings(string)
        
        if id == None and idType == None:
            id, idType = checkRegExStrings(string)
        
        if id == None and idType == None:
            vPrint("Is the string just numbers?")
            id = string
        checkInt = checkIfStringIsInteger(id)
        if checkInt == None:
            if id == "": self.type = None; return None
            vPrint("Setting type to rbxType.UNKNOWN")
            idType = rbxType.UNKNOWN
        else:
            id = checkInt

        self.id = id
        self.type = idType
        vPrint(self)
    
    def detectTypeFromId(self,ignore=[]) -> rbxType:
        id = self.id
        old_type = self.type
        vPrint(f"Attempt to detect type from {id} (Previous type was: {old_type})")

        vPrint("Badge?")
        if not rbxType.BADGE in ignore:
            badgeInfo = apiReqs.getBadgeInfo(id)
            if badgeInfo != False:
                self.type = rbxType.BADGE

        vPrint("Place?")
        if not rbxType.PLACE in ignore:
            economyInfo = apiReqs.getEconomyInfo(id)
            if economyInfo != False:
                # economy api is broad; check if the asset type is 9 (place)
                if economyInfo["AssetTypeId"] == 9:
                    self.type = rbxType.PLACE
        
        # universes, users and groups use a separate id system from places and badges, so one could be confused for the other.
        # when making a text file with minimal ids *please* use {type}::{id} to specify what type each id is!
        # otherwise, most if not all universe ids will get misjudged as a badge/place id.
        vPrint("Universe?")
        if not rbxType.UNIVERSE in ignore:
            universeInfo = apiReqs.getUniverseInfo(id)
            if universeInfo != False:
                self.type = rbxType.UNIVERSE

        if self.type == old_type:
            # tried everything? set to None and give up on this one
            vPrint("Mineral...? *shrug*")
            vPrint("Tried every type. Setting self.type to None.")
            self.type = None
        return self.type

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