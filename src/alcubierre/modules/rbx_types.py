# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/rbx_types.py
"""
Roblox asset type handling for alcubierre.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import re
from enum import Enum

from alcubierre.modules import api_reqs
from alcubierre.modules.verbose_print import vPrint, vvPrint


def check_if_string_is_integer(string: str):
    """
    Checks if the string is an integer or not.
    """
    vPrint(f"Checking if string {string} is an integer...")
    try:
        check_int = int(string)
        vPrint("String is an integer.")
        return check_int
    except ValueError:
        vPrint("String is not an integer.")
        return None


class RbxType(Enum):
    """
    Positive: singular item
    Negative: multiple items
    """
    def __str__(self):
        return self.name
    USER = -2
    GROUP = -1
    UNKNOWN = 0
    BADGE = 1
    PLACE = 2
    UNIVERSE = 3


TYPE_PATTERNS = {
    RbxType.PLACE: [
        re.compile(r"roblox\.com/games/(\d+)", re.IGNORECASE),
        re.compile(r"place\?id=(\d+)", re.IGNORECASE),
        re.compile(r"roblox\.com/Place\.aspx\?ID=(\d+)", re.IGNORECASE),
        re.compile(r"roblox\.com/PlaceItem\.aspx\?id=(\d+)", re.IGNORECASE)
    ],
    RbxType.BADGE: [
        re.compile(r"roblox\.com/badges/(\d+)", re.IGNORECASE),
        re.compile(r"item\?id=(\d+)", re.IGNORECASE)
    ],
    RbxType.GROUP: [
        re.compile(r"roblox\.com/groups/(\d+)", re.IGNORECASE),
    ],
    RbxType.USER: [
        re.compile(r"roblox\.com/users/(\d+)", re.IGNORECASE),
        re.compile(r"roblox\.com/User\.aspx\?ID=(\d+)", re.IGNORECASE)
    ]
}

TYPE_STRINGS = {
    RbxType.PLACE: [
        "place::", "places::", "p::",
        "game::", "games::"
    ],
    RbxType.BADGE: [
        "badge::", "badges::", "b::"
    ],
    RbxType.UNIVERSE: [
        "universe::", "universes::", "u::"
    ],
    RbxType.GROUP: [
        "group::", "groups::", "g::"
    ],
    RbxType.USER: [
        "user::", "users::", "u::",
        "player::", "players::"
    ]
}


def check_for_coloncolon_string(string: str):
    """
    Checks if a string is a colon-colon ('::') string.
    """
    for rbx_type, colon_strings in TYPE_STRINGS.items():
        vvPrint(f"Checking '::' strings for type: {rbx_type}")
        for colon_string in colon_strings:
            vvPrint(f"'::' string: {colon_string}")
            if colon_string in string:
                roblox_id = string.replace(colon_string, "")
                id_type = rbx_type
                return roblox_id, id_type
    return None, None


def check_regex_strings(string: str):
    """
    Checks if a string can be RegEx'd for a type.
    """
    for rbx_type, patterns in TYPE_PATTERNS.items():
        vvPrint(f"Checking patterns for type: {rbx_type}")
        for pattern in patterns:
            vvPrint(f"Pattern: {pattern}")
            match = pattern.search(string)
            if match:
                roblox_id = match.group(1)
                id_type = rbx_type
                return roblox_id, id_type
    return None, None


class RbxReason(Enum):
    """
    Positive: 'good' outcome
    Negative: 'bad' outcome
    """
    def __str__(self):
        return self.name

    BADGE_COLLECTED = 4
    TIME_UP = 3
    PROCESS_CLOSED = 2
    PROCESS_OPENED = 1
    ALREADY_COLLECTED = -1
    NOT_ENABLED = -2
    NO_BADGES_IN_UNIVERSE = -3
    ALREADY_PLAYED = -4
    NOT_PLAYABLE = -5
    NOT_ENOUGH_PLAYERS_AWARDED = -6
    NO_UNIVERSE = -7
    BAD_VOTE_RATIO = -8
    TOO_MANY_VISITS = -9


class RbxInstance:
    """
    A class for holding information for each line.
    """
    def __init__(self, roblox_id=None, asset_type=None):
        self.id = roblox_id
        self.type = asset_type
        self.info = None  # no info yet as it was just created

    def __str__(self):
        return f"RbxInstance [id: {self.id}, type: {self.type}]"

    def get_info_from_type(self):
        """
        Gets infomation from RbxType.
        """
        vPrint(f"Getting info for {self.id} with type {self.type}")
        info = False
        if self.type == RbxType.BADGE:
            info = api_reqs.get_badge_info(self.id)
        if self.type == RbxType.PLACE:
            info = api_reqs.get_place_info(self.id)
        if self.type == RbxType.UNIVERSE:
            info = api_reqs.get_universe_info(self.id)
        if self.type == RbxType.GROUP:
            info = api_reqs.get_group_info(self.id)
        if self.type == RbxType.USER:
            info = api_reqs.get_user_info(self.id)

        if info is not False:
            self.info = info
        return info

    def detect_string_type(self, string: str):
        """
        Goes through a bunch of checks to find what type the string is.
        """
        if not isinstance(string, str):
            self.type = None
            return None
        vPrint("Detecting type from string...")
        roblox_id = None
        id_type = None

        if "::" in string:
            roblox_id, id_type = check_for_coloncolon_string(string)

        if roblox_id is None and id_type is None:
            roblox_id, id_type = check_regex_strings(string)

        if roblox_id is None and id_type is None:
            if roblox_id == "":
                self.type = None
                return None
            vPrint("Is the string just numbers?")
            roblox_id = string
            check_int = check_if_string_is_integer(roblox_id)
            if check_int is None:
                self.type = None
                return None
            else:
                roblox_id = check_int
                vPrint("Setting type to rbxType.UNKNOWN")
                id_type = RbxType.UNKNOWN

        self.id = int(roblox_id)
        self.type = id_type
        vPrint(self)

    def detect_type_from_int(self, ignore=None) -> RbxType:
        """
        Detects RbxType from integer.
        """
        if ignore is None:
            ignore = []

        roblox_id = self.id
        old_type = self.type
        vPrint(f"Attempt to detect type from {roblox_id} (Previous type was: {old_type})")

        vPrint("Badge?")
        if RbxType.BADGE not in ignore:
            badge_info = api_reqs.get_badge_info(roblox_id)
            if badge_info is not False:
                self.type = RbxType.BADGE

        vPrint("Place?")
        if RbxType.PLACE not in ignore:
            economy_info = api_reqs.get_economy_info(roblox_id)
            if economy_info is not False:
                # economy api is broad; check if the asset type is 9 (place)
                if economy_info["AssetTypeId"] == 9:
                    self.type = RbxType.PLACE

        # universes, users and groups use a separate id system from places and badges, so one could be confused for the other.
        # when making a text file with minimal ids *please* use {type}::{id} to specify what type each id is!
        # otherwise, most if not all universe ids will get misjudged as a badge/place id.
        vPrint("Universe?")
        if RbxType.UNIVERSE not in ignore:
            universe_info = api_reqs.get_universe_info(roblox_id)
            if universe_info is not False:
                self.type = RbxType.UNIVERSE

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
