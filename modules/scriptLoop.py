# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/scriptLoop.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

import time
#import pygame

from . import apiReqs, dataSave, processHandle, playSound
from .rbxTypes import rbxInstance, rbxType, rbxReason
from .verbosePrint import vPrint

def dealWithBadge(badge_rbxInstance:rbxInstance,user_id=None,awardedThreshold=-1,voteThreshold=-1.0,open_place_in_browser=False,use_bloxstrap=True,use_sober=True,sober_opts="") -> rbxReason:
    badge_info = badge_rbxInstance.info
    rootPlaceId = badge_info["awardingUniverse"]["rootPlaceId"]
    badgeName = badge_info["name"]
    print(f"Badge Name: {badgeName}")

    if badge_rbxInstance.id in dataSave.gotten_badges:
        print("Badge in 'gotten_badges.json' list, skipping!")
        return rbxReason.alreadyCollected
    
    if rootPlaceId in dataSave.played_places:
        print(f"Skipping place {str(rootPlaceId)}; already played!")
        return rbxReason.alreadyPlayed

    awardedCount = badge_info["statistics"]["awardedCount"]
    if not awardedCount >= awardedThreshold:
        print(str(awardedCount) + " people with this badge is not enough for set threshold, skipping...")
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
    
    if voteThreshold != -1:
        universeVotes = apiReqs.getUniverseVotes(badge_info["awardingUniverse"]["id"])
        vPrint(f"universeVotes: {universeVotes}")
        uvRatio = int(universeVotes["upVotes"]) / int(universeVotes["downVotes"])
        vPrint(f"uvRatio: {uvRatio}")
        if uvRatio <= voteThreshold:
            print("Universe has a bad like-to-dislike ratio, skipping...")
            return rbxReason.badVoteRatio

    placeDetails = apiReqs.getPlaceInfo(rootPlaceId,noAlternative=True) # need the auth-only place api for playability stats
    if placeDetails != False:
        if placeDetails["isPlayable"] == False:
            print("Not playable, skipping!")
            return rbxReason.notPlayable

    if open_place_in_browser: processHandle.openPlaceInBrowser(rootPlaceId)

    processHandle.openRobloxPlace(
        rootPlaceId,
        name=badge_info["awardingUniverse"]["name"],
        use_bloxstrap=use_bloxstrap,
        use_sober=use_sober,
        sober_opts=sober_opts
        )
    return rbxReason.processOpened

def dealWithPlace(place_rbxInstance:rbxInstance,voteThreshold=-1.0,checkIfBadgesOnUniverse=True,open_place_in_browser=False,use_bloxstrap=True,use_sober=True,sober_opts="") -> rbxReason:
    place_Info = place_rbxInstance.info

    if checkIfBadgesOnUniverse:
        universeId = apiReqs.getUniverseFromPlaceId(place_rbxInstance.id)
        if universeId != None:
            check_universe_badges = apiReqs.checkUniverseForAnyBadges(universeId)
            if check_universe_badges == False:
                print("No badges found in the universe/place, skipping...")
                return rbxReason.noBadgesInUniverse
            if voteThreshold != -1:
                universeVotes = apiReqs.getUniverseVotes(universeId)
                vPrint(f"universeVotes: {universeVotes}")
                uvRatio = int(universeVotes["upVotes"]) / int(universeVotes["downVotes"])
                vPrint(f"uvRatio: {uvRatio}")
                if uvRatio <= voteThreshold:
                    print("Universe has a bad like-to-dislike ratio, skipping...")
                    return rbxReason.badVoteRatio

        else: # no universe means that it"s most likely *not* a place...
            return rbxReason.noUniverse
    
    if open_place_in_browser: processHandle.openPlaceInBrowser(place_rbxInstance.id)

    processHandle.openRobloxPlace(
        place_rbxInstance.id,
        name=place_Info["name"],
        use_bloxstrap=use_bloxstrap,
        use_sober=use_sober,
        sober_opts=sober_opts
        )
    return rbxReason.processOpened

def dealWithUniverse(universe_rbxInstance:rbxInstance,voteThreshold=-1.0,checkIfBadgesOnUniverse=True,open_place_in_browser=False,use_bloxstrap=True,use_sober=True,sober_opts="") -> rbxReason:
    universe_info = universe_rbxInstance.info
    rootPlaceId = universe_info["rootPlaceId"]

    if checkIfBadgesOnUniverse:
        check_universe_badges = apiReqs.checkUniverseForAnyBadges(universe_rbxInstance.id)
        if check_universe_badges == False:
            print("No badges found in the universe/place, skipping...")
            return rbxReason.noBadgesInUniverse
        
    if voteThreshold != -1:
        universeVotes = apiReqs.getUniverseVotes(universe_rbxInstance.id)
        vPrint(f"universeVotes: {universeVotes}")
        uvRatio = int(universeVotes["upVotes"]) / int(universeVotes["downVotes"])
        vPrint(f"uvRatio: {uvRatio}")
        if uvRatio <= voteThreshold:
            print("Universe has a bad like-to-dislike ratio, skipping...")
            return rbxReason.badVoteRatio
    
    placeDetails = apiReqs.getPlaceInfo(rootPlaceId,noAlternative=True) # need the auth-only place api for playability stats
    if placeDetails != False:
        if placeDetails["isPlayable"] == False:
            print("Not playable, skipping!")
            return rbxReason.notPlayable

    if open_place_in_browser: processHandle.openPlaceInBrowser(rootPlaceId)

    processHandle.openRobloxPlace(rootPlaceId,
        name=universe_info["name"],
        use_bloxstrap=use_bloxstrap,
        use_sober=use_sober,
        sober_opts=sober_opts
        )
    return rbxReason.processOpened

def dealWithInstance(an_rbxInstance:rbxInstance,user_id=None,awardedThreshold=-1,voteThreshold=-1.0,checkIfBadgesOnUniverse=True,open_place_in_browser=False,use_bloxstrap=True,use_sober=True,sober_opts="",nested=False) -> rbxReason:
    """
    Deals with rbxInstance; should either return a new process or rbxReason
    """
    result = None
    if an_rbxInstance.type == rbxType.BADGE:
        result = dealWithBadge(
            badge_rbxInstance=an_rbxInstance,
            user_id=user_id,
            awardedThreshold=awardedThreshold,
            voteThreshold=voteThreshold,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts
            )
    if an_rbxInstance.type == rbxType.PLACE:
        result = dealWithPlace(
            place_rbxInstance=an_rbxInstance,
            voteThreshold=voteThreshold,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts
            )
        if result == rbxReason.noUniverse:
            if nested == True: return False # already tried this; stop
            an_rbxInstance.detectTypeFromId()
            # and then go back again...
            vPrint("Time to do an inception on this instance...")
            return dealWithInstance(
                an_rbxInstance=an_rbxInstance,
                user_id=user_id,
                awardedThreshold=awardedThreshold,
                voteThreshold=voteThreshold,
                checkIfBadgesOnUniverse=checkIfBadgesOnUniverse,
                open_place_in_browser=open_place_in_browser,
                use_bloxstrap=use_bloxstrap,
                use_sober=use_sober,
                sober_opts=sober_opts,
                nested=True
                )
    if an_rbxInstance.type == rbxType.UNIVERSE:
        result = dealWithUniverse(
            universe_rbxInstance=an_rbxInstance,
            voteThreshold=voteThreshold,
            checkIfBadgesOnUniverse=checkIfBadgesOnUniverse,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts
            )
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

    if len(check_universe_badges) == 1: return True
    return False

dataSave.init()

def handleLine(line,user_id=None,awardedThreshold=-1,voteThreshold=-1.0,secs_reincarnation=-1,open_place_in_browser=False,use_bloxstrap=True,use_sober=True,sober_opts="",checkIfBadgesOnUniverse=True,detectOneBadgeUniverses=True):
    line_rbxInstance = rbxInstance()
    line_rbxInstance.stringIdThingy(line)

    if line_rbxInstance.id == None:
        return False
    
    if line_rbxInstance.id in dataSave.gotten_badges:
        print(f"Skipping {line}, already collected!")
        return rbxReason.alreadyCollected
    if line_rbxInstance.id in dataSave.played_places:
        print(f"Skipping {line}, already played!")
        return rbxReason.alreadyPlayed
    
    if line_rbxInstance.type == rbxType.UNKNOWN:
        line_rbxInstance.detectTypeFromId()
    if line_rbxInstance.type == None:
        return False
    
    vPrint(f"line_rbxInstance: {line_rbxInstance}")
    line_rbxInstance.getInfoFromType()
    #print(line_rbxInstance.type)

    if line_rbxInstance.type == rbxType.GROUP or line_rbxInstance.type == rbxType.USER:
        places = []
        if line_rbxInstance.type == rbxType.GROUP:
            places = apiReqs.findGroupPlaces(line_rbxInstance.id)
        if line_rbxInstance.type == rbxType.USER:
            places = apiReqs.findUserPlaces(line_rbxInstance.id)
        
        if places != []:
            for place_number, placeId in enumerate(places,start=1):
                print(f"Sub-place {str(place_number)}: {str(placeId)}")
                handleLine(
                    line=f"place::{str(placeId)}",
                    user_id=user_id,
                    awardedThreshold=awardedThreshold,
                    voteThreshold=voteThreshold,
                    secs_reincarnation=secs_reincarnation,
                    open_place_in_browser=open_place_in_browser,
                    use_bloxstrap=use_bloxstrap,
                    use_sober=use_sober,
                    sober_opts=sober_opts,
                    checkIfBadgesOnUniverse=checkIfBadgesOnUniverse,
                    detectOneBadgeUniverses=detectOneBadgeUniverses
                    )
    
    line_rbxReason = dealWithInstance(
        an_rbxInstance=line_rbxInstance,
        user_id=user_id,
        awardedThreshold=awardedThreshold,
        voteThreshold=voteThreshold,
        checkIfBadgesOnUniverse=checkIfBadgesOnUniverse,
        open_place_in_browser=open_place_in_browser,
        use_bloxstrap=use_bloxstrap,
        use_sober=use_sober,
        sober_opts=sober_opts
        )
    vPrint(f"line_rbxReason: {line_rbxReason}")

    if line_rbxReason == rbxReason.processOpened:
        singleBadge = False
        if line_rbxInstance.type == rbxType.BADGE and detectOneBadgeUniverses == True:
            if isUniverseOneBadge(line_rbxInstance):
                print("[SOLO BADGE! ONLY 1 TO COLLECT FOR THIS GAME!]")
                playSound.playSound("notify")
                singleBadge = True

        time.sleep(15)

        process_rbxReason = processHandle.waitForProcessOrBadgeCollect(line_rbxInstance,user_id,secs_reincarnation,singleBadge)
        vPrint(f"process_rbxReason: {process_rbxReason}")
        if process_rbxReason == rbxReason.badgeCollected:
            print("Badge has been awarded!")
            dataSave.gotten_badges.append(line_rbxInstance.id)
            dataSave.save_data(dataSave.gotten_badges,"gotten_badges.json")
            playSound.playSound("success")
            processHandle.kill_roblox_process()
    return True

def start(lines,user_id=None,awardedThreshold=-1,voteThreshold=-1.0,secs_reincarnation=-1,open_place_in_browser=False,use_bloxstrap=True,use_sober=True,sober_opts="",checkIfBadgesOnUniverse=True,detectOneBadgeUniverses=True):
    # check if variables are correctly set
    if not type(user_id) == int: user_id = None
    if not type(awardedThreshold) == int: awardedThreshold = -1
    if not type(voteThreshold) == float: voteThreshold = -1.0
    if not type(secs_reincarnation) == int: secs_reincarnation = -1
    if not type(open_place_in_browser) == bool: open_place_in_browser = False
    if not type(use_bloxstrap) == bool: use_bloxstrap = True
    if not type(use_sober) == bool: use_sober = True
    if not type(open_place_in_browser) == bool: open_place_in_browser = False
    if not type(checkIfBadgesOnUniverse) == bool: checkIfBadgesOnUniverse = True
    if not type(detectOneBadgeUniverses) == bool: detectOneBadgeUniverses = True
    
    for line_number, line in enumerate(lines,start=1):
        #print(line)
        stripped_line = line.strip()
        print(f"Line {line_number}: {stripped_line}")

        if stripped_line == "":
            vPrint("Empty line, skipping...")
            continue
        
        handleLine(
            line=stripped_line,
            user_id=user_id,
            awardedThreshold=awardedThreshold,
            voteThreshold=voteThreshold,
            secs_reincarnation=secs_reincarnation,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts,
            checkIfBadgesOnUniverse=checkIfBadgesOnUniverse,
            detectOneBadgeUniverses=detectOneBadgeUniverses
            )

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