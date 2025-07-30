# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/script_loop.py
"""
Main loop for alcubierre
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import time

from alcubierre.modules import api_reqs, data_save, play_sound, process_handle
from alcubierre.modules.rbx_types import RbxInstance, RbxType, RbxReason
from alcubierre.modules.verbose_print import vPrint, log_n_print


def deal_with_badge(badge_rbxinstance: RbxInstance, user_id=None, awarded_threshold=-1, vote_threshold=-1.0, open_place_in_browser=False, use_bloxstrap=True, use_sober=True, sober_opts="") -> RbxReason:
    """
    Deals with RbxInstances with RbxType.BADGE
    """
    badge_info = badge_rbxinstance.info
    root_place_id = badge_info["awardingUniverse"]["rootPlaceId"]
    badge_name = badge_info["name"]
    log_n_print(f"Badge Name: {badge_name}")

    if root_place_id in data_save.PLAYED_PLACES:
        log_n_print(f"Skipping place {str(root_place_id)}; already played!")
        return RbxReason.ALREADY_PLAYED

    awarded_count = badge_info["statistics"]["awardedCount"]
    if not awarded_count >= awarded_threshold:
        log_n_print(str(awarded_count) + " people with this badge is not enough for set threshold, skipping...")
        return RbxReason.NOT_ENOUGH_PLAYERS_AWARDED

    if badge_info["enabled"] is False:
        log_n_print("Badge is not enabled, skipping!")
        return RbxReason.NOT_ENABLED

    check_universe_badges = api_reqs.get_universe_badges_first_page(badge_info["awardingUniverse"]["id"])
    if not check_universe_badges:
        log_n_print("No badges found in the universe/place, skipping...")
        return RbxReason.NO_BADGES_IN_UNIVERSE

    if vote_threshold != -1:
        universe_votes = api_reqs.get_universe_votes(badge_info["awardingUniverse"]["id"])
        vPrint(f"universe_votes: {universe_votes}")
        uv_ratio = int(universe_votes["upVotes"]) / int(universe_votes["downVotes"])
        vPrint(f"uv_ratio: {uv_ratio}")
        if uv_ratio <= vote_threshold:
            log_n_print("Universe has a bad like-to-dislike ratio, skipping...")
            return RbxReason.BAD_VOTE_RATIO

    place_details = api_reqs.get_place_info(root_place_id, no_alternative=True)  # need the auth-only place api for playability stats
    if place_details:
        if not place_details["isPlayable"]:
            log_n_print("Not playable, skipping!")
            return RbxReason.NOT_PLAYABLE

    # we check if the user collected the badge last because we're not caching the responses for them
    if user_id is not None:
        check_inventory = api_reqs.check_user_inv_for_badge(user_id, badge_rbxinstance.id)
        if check_inventory:
            log_n_print("Badge has already been collected, skipping!")
            data_save.GOTTEN_BADGES.append(badge_rbxinstance.id)
            data_save.save_data(data_save.GOTTEN_BADGES, "gotten_badges.json")
            return RbxReason.ALREADY_COLLECTED

    if open_place_in_browser:
        process_handle.open_place_in_browser(root_place_id)

    process_handle.open_roblox_place(root_place_id,
                                     name=badge_info["awardingUniverse"]["name"],
                                     use_bloxstrap=use_bloxstrap,
                                     use_sober=use_sober,
                                     sober_opts=sober_opts
                                     )
    return RbxReason.PROCESS_OPENED


def deal_with_place(place_rbxinstance: RbxInstance, vote_threshold=-1.0, check_if_badges_on_universe=True, open_place_in_browser=False, use_bloxstrap=True, use_sober=True, sober_opts="") -> RbxReason:
    """
    Deals with RbxInstances with RbxType.PLACE
    """
    place_info = place_rbxinstance.info

    if check_if_badges_on_universe:
        universe_id = api_reqs.get_universe_from_place_id(place_rbxinstance.id)
        if universe_id is not None:
            check_universe_badges = api_reqs.get_universe_badges_first_page(universe_id)
            if not check_universe_badges:
                log_n_print("No badges found in the universe/place, skipping...")
                return RbxReason.NO_BADGES_IN_UNIVERSE
            if vote_threshold != -1:
                universe_votes = api_reqs.get_universe_votes(universe_id)
                vPrint(f"universe_votes: {universe_votes}")
                uv_ratio = int(universe_votes["upVotes"]) / int(universe_votes["downVotes"])
                vPrint(f"uv_ratio: {uv_ratio}")
                if uv_ratio <= vote_threshold:
                    log_n_print("Universe has a bad like-to-dislike ratio, skipping...")
                    return RbxReason.BAD_VOTE_RATIO

        else:  # no universe means that it"s most likely *not* a place...
            return RbxReason.NO_UNIVERSE

    if open_place_in_browser:
        process_handle.open_place_in_browser(place_rbxinstance.id)

    process_handle.open_roblox_place(place_rbxinstance.id,
                                     name=place_info["name"],
                                     use_bloxstrap=use_bloxstrap,
                                     use_sober=use_sober,
                                     sober_opts=sober_opts
                                     )
    return RbxReason.PROCESS_OPENED


def deal_with_universe(universe_rbxinstance: RbxInstance, vote_threshold=-1.0, check_if_badges_on_universe=True, open_place_in_browser=False, use_bloxstrap=True, use_sober=True, sober_opts="") -> RbxReason:
    """
    Deals with RbxInstances with RbxType.UNIVERSE
    """
    universe_info = universe_rbxinstance.info
    root_place_id = universe_info["rootPlaceId"]

    if check_if_badges_on_universe:
        check_universe_badges = api_reqs.get_universe_badges_first_page(universe_rbxinstance.id)
        if not check_universe_badges:
            log_n_print("No badges found in the universe/place, skipping...")
            return RbxReason.NO_BADGES_IN_UNIVERSE

    if vote_threshold != -1:
        universe_votes = api_reqs.get_universe_votes(universe_rbxinstance.id)
        vPrint(f"universe_votes: {universe_votes}")
        uv_ratio = int(universe_votes["upVotes"]) / int(universe_votes["downVotes"])
        vPrint(f"uv_ratio: {uv_ratio}")
        if uv_ratio <= vote_threshold:
            log_n_print("Universe has a bad like-to-dislike ratio, skipping...")
            return RbxReason.BAD_VOTE_RATIO

    place_details = api_reqs.get_place_info(root_place_id, no_alternative=True)  # need the auth-only place api for playability stats
    if place_details:
        if not place_details["isPlayable"]:
            log_n_print("Not playable, skipping!")
            return RbxReason.NOT_PLAYABLE

    if open_place_in_browser:
        process_handle.open_place_in_browser(root_place_id)

    process_handle.open_roblox_place(root_place_id,
                                     name=universe_info["name"],
                                     use_bloxstrap=use_bloxstrap,
                                     use_sober=use_sober,
                                     sober_opts=sober_opts
                                     )
    return RbxReason.PROCESS_OPENED


def deal_with_rbxinstance(an_rbxinstance: RbxInstance, user_id=None, awarded_threshold=-1, vote_threshold=-1.0, check_if_badges_on_universe=True, open_place_in_browser=False, use_bloxstrap=True, use_sober=True, sober_opts="", nested=False) -> RbxReason:
    """
    Deals with rbxInstance; should either return a new process or rbxReason
    """
    result = None
    if an_rbxinstance.type == RbxType.BADGE:
        result = deal_with_badge(
            badge_rbxinstance=an_rbxinstance,
            user_id=user_id,
            awarded_threshold=awarded_threshold,
            vote_threshold=vote_threshold,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts
            )
    if an_rbxinstance.type == RbxType.PLACE:
        result = deal_with_place(
            place_rbxinstance=an_rbxinstance,
            vote_threshold=vote_threshold,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts
            )
        if result == RbxReason.NO_UNIVERSE:
            if nested:
                return False  # already tried this; stop
            an_rbxinstance.detect_type_from_int()
            # and then go back again...
            vPrint("Time to do an inception on this instance...")
            return deal_with_rbxinstance(
                an_rbxinstance=an_rbxinstance,
                user_id=user_id,
                awarded_threshold=awarded_threshold,
                vote_threshold=vote_threshold,
                check_if_badges_on_universe=check_if_badges_on_universe,
                open_place_in_browser=open_place_in_browser,
                use_bloxstrap=use_bloxstrap,
                use_sober=use_sober,
                sober_opts=sober_opts,
                nested=True
                )
    if an_rbxinstance.type == RbxType.UNIVERSE:
        result = deal_with_universe(
            universe_rbxinstance=an_rbxinstance,
            vote_threshold=vote_threshold,
            check_if_badges_on_universe=check_if_badges_on_universe,
            open_place_in_browser=open_place_in_browser,
            use_bloxstrap=use_bloxstrap,
            use_sober=use_sober,
            sober_opts=sober_opts
            )
    return result


def is_universe_one_badge(an_rbxinstance: RbxInstance) -> bool:
    """
    This should be for *after* dealWithInstance(), not before. This is so the tempRespCache from apiReqs get used.
    """
    check_universe_badges = ""
    if an_rbxinstance.type == RbxType.BADGE:
        check_universe_badges = api_reqs.get_universe_badges_first_page(an_rbxinstance.info["awardingUniverse"]["id"])
    if an_rbxinstance.type == RbxType.PLACE:
        universe_id = api_reqs.get_universe_from_place_id(an_rbxinstance.id)
        check_universe_badges = api_reqs.get_universe_badges_first_page(universe_id)
    if an_rbxinstance.type == RbxType.UNIVERSE:
        check_universe_badges = api_reqs.get_universe_badges_first_page(an_rbxinstance.id)

    if len(check_universe_badges) == 1:
        return True
    return False


def handle_line(line, user_id=None, awarded_threshold=-1, vote_threshold=-1.0, secs_reincarnation=-1, open_place_in_browser=False, use_bloxstrap=True, use_sober=True, sober_opts="", check_if_badges_on_universe=True, detect_one_badge_universes=True):
    """
    Handles lines from text file.
    """
    line_rbxinstance = RbxInstance()
    line_rbxinstance.detect_string_type(line)

    if line_rbxinstance.id is None:
        return False

    if line_rbxinstance.id in data_save.GOTTEN_BADGES:
        log_n_print(f"Skipping {line}, already collected!")
        return RbxReason.ALREADY_COLLECTED
    if line_rbxinstance.id in data_save.PLAYED_PLACES:
        log_n_print(f"Skipping {line}, already played!")
        return RbxReason.ALREADY_PLAYED

    if line_rbxinstance.type == RbxType.UNKNOWN:
        line_rbxinstance.detect_type_from_int()
    if line_rbxinstance.type is None:
        return False

    vPrint(f"line_rbxinstance: {line_rbxinstance}")
    line_rbxinstance.get_info_from_type()
    # print(line_rbxInstance.type)

    if line_rbxinstance.type == RbxType.GROUP or line_rbxinstance.type == RbxType.USER:
        places = []
        if line_rbxinstance.type == RbxType.GROUP:
            places = api_reqs.find_group_places(line_rbxinstance.id)
        if line_rbxinstance.type == RbxType.USER:
            places = api_reqs.find_user_places(line_rbxinstance.id)

        if places != []:
            for place_number, place_id in enumerate(places, start=1):
                log_n_print(f"Sub-place {str(place_number)}: {str(place_id)}")
                handle_line(
                    line=f"place::{str(place_id)}",
                    user_id=user_id,
                    awarded_threshold=awarded_threshold,
                    vote_threshold=vote_threshold,
                    secs_reincarnation=secs_reincarnation,
                    open_place_in_browser=open_place_in_browser,
                    use_bloxstrap=use_bloxstrap,
                    use_sober=use_sober,
                    sober_opts=sober_opts,
                    check_if_badges_on_universe=check_if_badges_on_universe,
                    detect_one_badge_universes=detect_one_badge_universes
                    )

    line_rbxreason = deal_with_rbxinstance(an_rbxinstance=line_rbxinstance,
                                           user_id=user_id,
                                           awarded_threshold=awarded_threshold,
                                           vote_threshold=vote_threshold,
                                           check_if_badges_on_universe=check_if_badges_on_universe,
                                           open_place_in_browser=open_place_in_browser,
                                           use_bloxstrap=use_bloxstrap,
                                           use_sober=use_sober,
                                           sober_opts=sober_opts
                                           )
    vPrint(f"line_rbxreason: {line_rbxreason}")

    if line_rbxreason == RbxReason.PROCESS_OPENED:
        single_badge = False
        if line_rbxinstance.type == RbxType.BADGE and detect_one_badge_universes is True:
            if is_universe_one_badge(line_rbxinstance):
                log_n_print("[SOLO BADGE! ONLY 1 TO COLLECT FOR THIS GAME!]")
                play_sound.play_sound("notify")
                single_badge = True

        time.sleep(15)

        process_rbxreason = process_handle.wait_for_process_or_badge_collect(line_rbxinstance, user_id, secs_reincarnation, single_badge)
        vPrint(f"process_rbxreason: {process_rbxreason}")
        if process_rbxreason == RbxReason.BADGE_COLLECTED:
            log_n_print("Badge has been awarded!")
            data_save.GOTTEN_BADGES.append(line_rbxinstance.id)
            data_save.save_data(data_save.GOTTEN_BADGES, "gotten_badges.json")
            play_sound.play_sound("success")
            process_handle.kill_roblox_process()
    return True


def start(lines, user_id=None, awarded_threshold=-1, vote_threshold=-1.0, secs_reincarnation=-1, open_place_in_browser=False, use_bloxstrap=True, use_sober=True, sober_opts="", check_if_badges_on_universe=True, detect_one_badge_universes=True):
    """
    'Start from lines, give what needs to be new'
    """
    # check if variables are correctly set
    if not isinstance(user_id, int):
        user_id = None
    if not isinstance(awarded_threshold, int):
        awarded_threshold = -1
    if not isinstance(vote_threshold, float):
        vote_threshold = -1.0
    if not isinstance(secs_reincarnation, int):
        secs_reincarnation = -1
    if not isinstance(open_place_in_browser, bool):
        open_place_in_browser = False
    if not isinstance(use_bloxstrap, bool):
        use_bloxstrap = True
    if not isinstance(use_sober, bool):
        use_sober = True
    if not isinstance(open_place_in_browser, bool):
        open_place_in_browser = False
    if not isinstance(check_if_badges_on_universe, bool):
        check_if_badges_on_universe = True
    if not isinstance(detect_one_badge_universes, bool):
        detect_one_badge_universes = True

    for line_number, line in enumerate(lines, start=1):
        # print(line)
        stripped_line = line.strip()
        log_n_print(f"Line {line_number}: {stripped_line}")

        if stripped_line == "":
            vPrint("Empty line, skipping...")
            continue

        handle_line(line=stripped_line,
                    user_id=user_id,
                    awarded_threshold=awarded_threshold,
                    vote_threshold=vote_threshold,
                    secs_reincarnation=secs_reincarnation,
                    open_place_in_browser=open_place_in_browser,
                    use_bloxstrap=use_bloxstrap,
                    use_sober=use_sober,
                    sober_opts=sober_opts,
                    check_if_badges_on_universe=check_if_badges_on_universe,
                    detect_one_badge_universes=detect_one_badge_universes
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
