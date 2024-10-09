import os
from urllib.parse import unquote, urlparse
import pathlib #import PurePosixPath
import time
import webbrowser
import subprocess
import json
#import pygame

from . import apiReqs, dataSave, processHandle
from .rbxTypes import rbxInstance, rbxType, rbxReason
from .verbosePrint import vPrint

def dealWithBadge(badge_rbxInstance:rbxInstance,user_id=None,awardedThreshold=-1) -> rbxReason:
    badge_info = badge_rbxInstance.info
    rootPlaceId = badge_info["awardingUniverse"]["rootPlaceId"]
    badgeName = badge_info["name"]
    #vPrint(f"Badge Name: {badgeName}")

    if badge_rbxInstance.id in dataSave.gotten_badges:
        print("Badge in 'gotten_badges.json' list, skipping!")
        return rbxReason.alreadyCollected
    
    if rootPlaceId in dataSave.played_places:
        print(f"Skipping place {str(rootPlaceId)}; already played!")
        return rbxReason.alreadyPlayed

    awardedCount = badge_info["statistics"]["awardedCount"]
    if not awardedCount >= awardedThreshold:
        print(str(awardedCount) + " people with this badge is too little of a number, skipping...")
        return rbxReason.notEnoughPlayersAwarded

    if badge_info["enabled"] == False:
        print("Badge is not enabled, skipping!")
        return rbxReason.notEnabled

    if user_id != None:
        check_inventory = apiReqs.checkUserInvForAsset(user_id,badge_rbxInstance.id)
        if check_inventory == True:
            print("Badge has already been collected, skipping!")
            dataSave.gotten_badges.append(badge_rbxInstance.id)
            dataSave.save_data(dataSave.gotten_badges,"gotten_badges.json")
            return rbxReason.alreadyCollected

    check_universe_badges = apiReqs.checkUniverseForAnyBadges(badge_info["awardingUniverse"]["id"])
    if check_universe_badges == False:
        print("No badges found in the universe/place, skipping...")
        return rbxReason.noBadgesInUniverse
    
    placeDetails = apiReqs.getPlaceInfo(rootPlaceId,noAlternative=True) # need the auth-only place api for playability stats
    if placeDetails != False:
        if placeDetails["isPlayable"] == False:
            print("Not playable, skipping!")
            return rbxReason.notPlayable

    processHandle.openRobloxPlace(rootPlaceId,name=badge_info["awardingUniverse"]["name"])
    return rbxReason.processOpened

def dealWithPlace(place_rbxInstance:rbxInstance,checkIfBadgesOnUniverse=True) -> rbxReason:
    place_Info = place_rbxInstance.info

    if checkIfBadgesOnUniverse:
        universeId = apiReqs.getUniverseFromPlaceId(place_rbxInstance.id)
        if universeId != None:
            check_universe_badges = apiReqs.checkUniverseForAnyBadges(universeId)
            if check_universe_badges == False:
                print("No badges found in the universe/place, skipping...")
                return rbxReason.noBadgesInUniverse
        else: # no universe means that it"s most likely *not* a place...
            return rbxReason.noUniverse
    
    processHandle.openRobloxPlace(place_rbxInstance.id,name=place_Info["name"])
    return rbxReason.processOpened

def dealWithUniverse(universe_rbxInstance:rbxInstance,checkIfBadgesOnUniverse=True) -> rbxReason:
    universe_info = universe_rbxInstance.info
    rootPlaceId = universe_info["rootPlaceId"]

    if checkIfBadgesOnUniverse:
        check_universe_badges = apiReqs.checkUniverseForAnyBadges(universe_rbxInstance.id)
        if check_universe_badges == False:
            print("No badges found in the universe/place, skipping...")
            return rbxReason.noBadgesInUniverse
    
    placeDetails = apiReqs.getPlaceInfo(rootPlaceId,noAlternative=True) # need the auth-only place api for playability stats
    if placeDetails != False:
        if placeDetails["isPlayable"] == False:
            print("Not playable, skipping!")
            return rbxReason.notPlayable

    processHandle.openRobloxPlace(rootPlaceId,name=universe_info["name"])
    return rbxReason.processOpened

def dealWithInstance(an_rbxInstance:rbxInstance,user_id=None,awardedThreshold=-1,checkIfBadgesOnUniverse=True,nested=False) -> rbxReason:
    """
    Deals with rbxInstance; should either return a new process or rbxReason
    """
    if an_rbxInstance.type == rbxType.BADGE:
        result = dealWithBadge(an_rbxInstance,user_id,awardedThreshold)
    if an_rbxInstance.type == rbxType.PLACE:
        result = dealWithPlace(an_rbxInstance)
        if result == rbxReason.noUniverse:
            if nested == True: # already tried this; stop
                return False
            an_rbxInstance.detectTypeFromId()
            # and then go back again...
            vPrint("Time to do an inception on this instance...")
            return dealWithInstance(an_rbxInstance,user_id,awardedThreshold,checkIfBadgesOnUniverse,nested=True)
    if an_rbxInstance.type == rbxType.UNIVERSE:
        result = dealWithUniverse(an_rbxInstance,checkIfBadgesOnUniverse)
    return result

def isUniverseOneBadge(an_rbxInstance:rbxInstance) -> bool:
    """
    This should be for *after* dealWithInstance(), not before. This is so the tempRespCache from apiReqs get used.
    """
    if an_rbxInstance.type == rbxType.BADGE:
        check_universe_badges = apiReqs.checkUniverseForAnyBadges(an_rbxInstance.info["awardingUniverse"]["id"])
    if an_rbxInstance.type == rbxType.PLACE:
        universeId = apiReqs.getUniverseFromPlaceId(an_rbxInstance.id)
        check_universe_badges = apiReqs.checkUniverseForAnyBadges(universeId)
    if an_rbxInstance.type == rbxType.UNIVERSE:
        check_universe_badges = apiReqs.checkUniverseForAnyBadges(an_rbxInstance.id)

    if len(check_universe_badges) == 1:
        return True
    else:
        return False

dataSave.init()

def start(lines,user_id=None,awardedThreshold=-1,secs_reincarnation=-1,open_place_in_browser=False,use_bloxstrap=True,checkIfBadgesOnUniverse=True,detectOneBadgeUniverses=True):
    # check if variables are correctly set
    if not type(awardedThreshold) == int:
        awardedThreshold = -1
    if not type(secs_reincarnation) == int:
        secs_reincarnation = -1
    if not type(open_place_in_browser) == bool:
        open_place_in_browser = False
    if not type(use_bloxstrap) == bool:
        use_bloxstrap = True
    
    for line_number, line in enumerate(lines,start=1):
        #print(line)
        stripped_line = line.strip()
        print(f"Line {line_number}: {stripped_line}")

        line_rbxInstance = rbxInstance()
        line_rbxInstance.stringIdThingy(stripped_line)
        if line_rbxInstance.id == None:
            continue
        if line_rbxInstance.id in dataSave.gotten_badges:
            print(f"Skipping {stripped_line}, already collected!")
            continue
        if line_rbxInstance.id in dataSave.played_places:
            print(f"Skipping {stripped_line}, already played!")
            continue
        if line_rbxInstance.type == rbxType.UNKNOWN:
            line_rbxInstance.detectTypeFromId()
        if line_rbxInstance.type == None:
            continue

        print(f"line_rbxInstance; {line_rbxInstance}")
        line_rbxInstance.getInfoFromType()
        #print(line_rbxInstance.type)
        
        line_rbxReason = dealWithInstance(line_rbxInstance,user_id,awardedThreshold,checkIfBadgesOnUniverse)

        if line_rbxReason == rbxReason.processOpened:
            singleBadge = False
            if detectOneBadgeUniverses == True:
                if isUniverseOneBadge(line_rbxInstance):
                    print("[SOLO BADGE! ONLY 1 TO COLLECT FOR THIS GAME!]")
                    singleBadge = True

            time.sleep(15)

            process_rbxReason = processHandle.waitForProcessOrBadgeCollect(line_rbxInstance,user_id,secs_reincarnation,singleBadge)
            if process_rbxReason == rbxReason.badgeCollected:
                print("Badge has been awarded!")
                dataSave.gotten_badges.append(line_rbxInstance.id)
                dataSave.save_data(dataSave.gotten_badges,"gotten_badges.json")