# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./__main__.py
"""
Roblox Badge-to-Badge Place Teleporter
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import os
import re
import sys
import argparse
import time
import logging
from alcubierre.modules import api_reqs
from alcubierre.modules.verbose_print import toggle_verbose_print, toggle_very_verbose_print, log_n_print

__prog__ = "alcubierre"
__desc__ = "Teleports to every place on a file."
__version__ = "v1.0.0-dev"
__author__ = "exurd"
__copyright__ = "copyright (c) 2024, exurd"
__credits__ = ["exurd"]
__license__ = "GPL"
__short_license__ = """This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; check help (`-h`) for details.
"""
__long_license__ = """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>."""

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
    base_cache_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)
    base_cache_path = os.path.dirname(__file__)

URL_PATTERN = re.compile(r"https?://")


logging.basicConfig(filename="alcubierre.log",
                    filemode="a",
                    format="%(asctime)s,%(msecs)d %(levelname)s %(message)s",
                    datefmt="%H:%M:%S",
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("New log started!")


def file_or_url(path):
    """
    Detects if the path given is a file or url.
    Heavily warns the user if it's a URL.
    """
    if URL_PATTERN.match(path):
        print(f"The input appears to be a URL: {path}\nDownloading files without checking them can allow XSS injection or joining a game that could ban your account!\nIt is HIGHLY RECOMMENDED to download the file yourself, inspect what games you're going to join and clean up any misconfigured lines.")
        time.sleep(10)
        confirm = input("Do you *really* want to download the file? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborting.")
            sys.exit(1)
        return path
    try:
        return open(path, "r", encoding="utf-8")
    except OSError as e:
        raise argparse.ArgumentTypeError(f"Cannot open file: {e}")


def get_parser() -> argparse.ArgumentParser:
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser(
        prog=__prog__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__desc__,
        epilog=__long_license__
    )
    version = "%(prog)s " + __version__
    parser.add_argument("--version", action="version", version=version)

    parser.add_argument("file_path", nargs="?", type=file_or_url, default=None,
                        help="Filename path of Badge IDs/URLs.")

    parser.add_argument("--env-file", "-e", default=None,  # type=argparse.FileType("w"),
                        help=f"An .env file allows you to specify settings (the below options) for {parser.prog} to follow without cluttering the terminal or risking important tokens. If the file doesn't exist, the program will create a template in its place. More information on .env files can be found in the README.")
    # The .env file will allow you to check if the place is playable or not.
    # Caution: To create an .env file, you will need your account's Roblox cookies, which can pose a risk if someone hacks into your computer.
    # It should have the following:
    # ROBLOXTOKEN=""
    # USERAGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    parser.add_argument("--rbx-token", "-t", default=None,
                        help=".ROBLOSECURITY token. By using this option, you agree that this is your unique token and not anyone else's. DO NOT SHARE YOUR ROBLOX TOKEN WITH ANYONE! More info can be found here: https://ro.py.jmk.gg/dev/tutorials/roblosecurity/")

    parser.add_argument("--user-id", "-u", type=int, default=None,
                        help="Specify a Roblox User ID to check inventory for badges. Not required if you're already using --rbx-token. The User ID argument takes priority from --rbx-token.")
    # Your Roblox User ID. It can be found your profile. If set to 0 it will not use any features that need your User ID, like badge checking.
    # Example: mrflimflam --> https://www.roblox.com/users/339310190/profile --> 339310190
    #                                                     [---------]

    parser.add_argument("--awarded-threshold", "-at", type=int, default=-1, metavar="NUMBER",
                        help="Threshold of players with the badge. If the badge has a lower number than the threshold, it gets skipped. Setting to -1 (default) disables the threshold.")
    # How many players the badge has to reach before you get teleported to the game. Great for games that never had their badges implemented.
    # It can be set to any number. 10, 50, 100, 3000, 25000; whatever you think is the right amount of total users who won it validates the badge.
    # If you want all badges to go through, then set it to -1

    parser.add_argument("--vote-threshold", "-vt", type=float, default=-1, metavar="RATIO",
                        help="Threshold ratio of likes and dislikes. If a game has a lower ratio than the threshold, it gets skipped. Setting to -1 (default) disables the threshold.")

    parser.add_argument("--seconds", "-s", type=int, default=-1,
                        help="How many seconds before killing the Roblox process. Setting to -1 (default) disables the timer.")
    # How long until you join the next game.
    # 45 seconds is long enough if you're only looking around for the welcome badge when joining the games.
    # If you want more time, say, to look around in the game, try 5-10 minutes (300-600 seconds)

    parser.add_argument("--no-bloxstrap", "-nbs", action="store_false",
                        help="Windows only! Don't use Bloxstrap to open Roblox (not recommended). When this option is not in use, the program automagically detects if Bloxstrap is installed and uses it if so. Bloxstrap website: https://bloxstraplabs.com")

    parser.add_argument("--no-sober", "-nsob", action="store_false",
                        help="Linux only! Don't use Sober to open Roblox. When this option is not in use, the program automagically detects if Sober is installed and uses it if so. Sober website: https://sober.vinegarhq.org")

    parser.add_argument("--sober-opts", "-sopts", default="",
                        help="Linux only! Commands to give Sober. Connect with an equal sign for it to work (`--sober-opts='--opengl'`) See --no-sober for more info on Sober.")

    parser.add_argument("--open-in-browser", "-ob", action="store_true",
                        help="Opens the Roblox place in the default browser. Highly recommended, but set to False as default.")
    # Opens the URL to the place in your web browser as you join, so you can track the badges you need to collect. Simple as.

    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose mode. Prints out things to help with debugging.")

    parser.add_argument("--very-verbose", "-vv", action="store_true",
                        help="Very verbose mode. Print out as many things as it can to help with debugging. Not recommended as it can slow down the program.")

    # parser.add_argument("--do-not-skip", "-dns", action="store_false",
    #                 help="")

    parser.add_argument("--no-detect-one-badge", "-ndob", action="store_false",
                        help="Turns off one badge place detection, which automatically closes Roblox after the user has collected the solo badge on a place.")

    parser.add_argument("--cache-directory", "-cd", default=os.path.join(base_cache_path, "alcubierre_cache"),
                        help="The directory where cache data is kept.")

    parser.add_argument("--user-agent", "-ua", default=f"{parser.prog} - badge-to-badge teleporter {__version__}",
                        help="Sets the user agent for requests made by the program.")

    parser.add_argument("--save-response-cache", "-src", action="store_true",
                        help="Save API responses from Roblox into a file. This can save bandwidth, at the cost of new information from already checked responses being ignored.")

    parser.add_argument("--play-sound", "-ps", action="store_true",
                        help="Play sounds for important context.")

    parser.add_argument("--sound-pack", type=str, default="piano",
                        help=f"Sound packs to choose from: {os.listdir(os.path.join(base_path, 'sounds'))}")

    parser.description += f"\n\nThere are {str(len(parser._actions) - 1)} arguments available."

    return parser


def main(args=None):
    """
    Main function for alcubierre.
    """
    parser = get_parser()
    args = parser.parse_args(args)
    # print(args)

    print(f"{__prog__} {__version__}\n{__copyright__}\n\n{__short_license__}")

    if args.verbose or args.very_verbose:
        toggle_verbose_print()
    if args.very_verbose:
        toggle_very_verbose_print()

    from alcubierre.modules.verbose_print import vPrint, vvPrint
    vPrint("Verbose mode is now enabled, else you wouldn't be seeing this...")
    vvPrint("Very verbose mode is also enabled... Have fun!")

    if args.play_sound:
        from alcubierre.modules import play_sound
        play_sound.toggle_sound(args.sound_pack)
        vvPrint(play_sound.ACTIVE_SND_PACK)
        play_sound.play_sound("startup")

    vPrint("-------------------------")
    vPrint(f"Timestamp: {time.time()}")
    vPrint(f"Version: {__version__}")
    vvPrint("----")
    vvPrint("Current Args:")
    for arg in vars(args):
        if arg == "rbx_token":  # don't save the rbx token in the log! 
            continue
        vvPrint(f"{arg}: {getattr(args, arg)}")
    vPrint("-------------------------")

    user_agent = args.user_agent
    rbx_token = args.rbx_token

    env_file = args.env_file
    if env_file is not None:
        from alcubierre.modules import load_env
        if not os.path.isfile(env_file):
            load_env.create_env_template(parser, env_file)
            print(".env file was successfully created! Use a text editor to edit")
            sys.exit(0)
        else:
            vPrint(f"Loading .env file [{args.env_file}]...")
            data = load_env.load_env_file(env_file)
            if rbx_token == parser.get_default("RBX_TOKEN"):
                if "RBX_TOKEN" in data and data["USER_AGENT"] != "":
                    rbx_token = data["RBX_TOKEN"]

            if user_agent == parser.get_default("USER_AGENT"):
                if "USER_AGENT" in data and data["USER_AGENT"] != "":
                    user_agent = data["USER_AGENT"]

    from alcubierre.modules import data_save

    if args.file_path is None:
        parser.error("the following arguments are required to continue: file_path")

    lines = []
    if isinstance(args.file_path, str):
        log_n_print(f"URL provided: {args.file_path}")
        url_check = api_reqs.get_request_url(args.file_path, cache_results=False)
        if url_check.ok:
            lines = url_check.text.splitlines()
    else:
        log_n_print(f"File loaded: {args.file_path.name}")
        lines = args.file_path.read().splitlines()
        args.file_path.close()

    api_reqs.init(user_agent, rbx_token)

    user_id = args.user_id
    if user_id == parser.get_default("user_id") and api_reqs.is_token_cookie_there():
        user_info = api_reqs.get_user_from_token()
        vPrint(f"userInfo: [{user_info}]")
        user_id = user_info["id"]

    data_folder = data_save.get_data_file_path(args.cache_directory)
    if user_id != parser.get_default("user_id"):
        data_folder = os.path.join(data_folder, str(user_id))
    else:
        data_folder = os.path.join(data_folder, "guest")
    data_folder = data_save.get_data_file_path(data_folder)

    if args.save_response_cache:
        api_reqs.get_perm_cache()

    vPrint("Starting scriptLoop...")
    from alcubierre.modules import script_loop
    script_loop.start(
        lines,
        user_id=user_id,
        awarded_threshold=args.awarded_threshold,
        vote_threshold=args.vote_threshold,
        secs_reincarnation=args.seconds,
        open_place_in_browser=args.open_in_browser,
        use_bloxstrap=args.no_bloxstrap,
        use_sober=args.no_sober,
        sober_opts=args.sober_opts,
        detect_one_badge_universes=args.no_detect_one_badge
        )


if __name__ == "__main__":
    main()

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
