import os, sys, argparse, time
from modules.verbosePrint import toggleVerbosity

__prog__ = "alcubierre" 
__desc__ = "Teleports to every place on a file."
__version__ = "(git master branch)"
__author__ = "exurd"

def get_parser() -> argparse.ArgumentParser:
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=__desc__
    )
    version = "%(prog)s " + __version__
    parser.add_argument("--version", action="version", version=version)
    
    parser.add_argument("file_path", nargs="?", type=argparse.FileType("r"), default=None,
                        help="Filename path of Badge IDs/URLs.")
    
    parser.add_argument("--env-file", "-e", default=None, #type=argparse.FileType("w"),
                    help=f"An .env file allows you to specify settings (the below options) for {parser.prog} to follow without cluttering or risking leaking commands. If the file doesn't exist, the program will create a template in it's place. More infomation on .env files can be found in the README.")
    # The .env file will allow you to check if the place is playable or not.
    # Caution: To create an .env file, you will need your account's Roblox cookies, which can pose a risk if someone hacks into your computer.
    # It should have the following:
    #ROBLOXTOKEN=""
    #USERAGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    parser.add_argument("--rbx-token", "-t", default=None,
                    help=".ROBLOSECURITY token. By using this option, you agree that this is your unique token and not anyone else's. DO NOT SHARE YOUR ROBLOX TOKEN WITH ANYONE! More info can be found here: https://ro.py.jmk.gg/dev/tutorials/roblosecurity/")
    
    parser.add_argument("--user-id", "-u", type=int, default=None,
                    help="Specifys a Roblox User ID to check inventory for badges. Not required if you're already using --rbx-token, but the User ID does take priority when in used.")
    # Your Roblox User ID. It can be found your profile. If set to 0 it will not use any features that need your User ID, like badge checking.
    # Example: mrflimflam --> https://www.roblox.com/users/339310190/profile --> 339310190
    #                                                     [---------]

    parser.add_argument("--awarded-threshold", "-at", type=int, default=-1,
                    help="Threshold of players with the badge. If lower than the number specified, it gets skipped. Setting to -1 disables the threshold.")
    # How many players the badge has to reach before you get teleported to the game. Great for games that never had their badges implemented.
    # It can be set to any number. 10, 50, 100, 3000, 25000; whatever you think is the right amount of total users who won it validates the badge.
    # If you want all badges to go through, then set it to -1
    
    parser.add_argument("--seconds", "-s", type=int, default=-1,
                    help="How many seconds before script kills Roblox process and goes to next line in file. Setting to -1 or 0 disables the timer.")
    # How long until you join the next game.
    # 45 seconds is long enough if you're only looking around for the welcome badge when joining the games.
    # If you want more time, say, to look around in the game, try 5-10 minutes (300-600 seconds)

    parser.add_argument("--no-bloxstrap", "-nbs", action="store_false",
                    help="Windows only! Don't use Bloxstrap to open Roblox (not recommended). When this option is not in use, the script automagically detects if Bloxstrap is installed and uses it if so. Bloxstrap website: https://bloxstraplabs.com")
    
    parser.add_argument("--no-sober", "-nsob", action="store_false",
                    help="Linux only! Don't use Sober to open Roblox. When this option is not in use, the script automagically detects if Sober is installed and uses it if so. Sober website: https://sober.vinegarhq.org")
    
    parser.add_argument("--sober-opts", "-sopts", default="",
                    help="Linux only! Commands to give Sober. Connect with an equal sign for it to work (`--sober-opts='--opengl'`) See --no-sober for more info on Sober.")
    
    parser.add_argument("--open-in-browser", "-ob", action="store_true",
                    help="Opens the Roblox place in default browser. Highly recommended, but set False as default.")
    # Opens the URL to the place in your web browser as you join, so you can track the badges you need to collect. Simple as.
    
    parser.add_argument("--verbose", "-v", action="store_true",
                    help="Verbose mode. Print out as many things that can help with debugging.")

    # parser.add_argument("--do-not-skip", "-dns", action="store_false",
    #                 help="")

    parser.add_argument("--detect-one-badge-games", "-dobg", action="store_false",
                    help="Detects one badge games and automatically closes Roblox when the badge is collected.")

    parser.add_argument("--cache-directory", "-cd", default=os.path.join(os.path.dirname(__file__), "alcubierre_cache"),
                        help="The directory where caches/saved data is kept.")

    parser.add_argument("--user-agent", "-ua", default=f"{parser.prog} - badge-to-badge teleporter {__version__}",
                    help="Sets the user agent for requests made by the program.")

    return parser

# --play-sound FILE (optional)

def main(args=None):
    parser = get_parser()
    args = parser.parse_args(args)
    #print(args)

    if args.verbose:
        toggleVerbosity()
    from modules.verbosePrint import vPrint

    vPrint("-------------------------")
    vPrint(f"Timestamp: {time.time()}")
    vPrint(f"Version: {__version__}")
    vPrint(f"Current Args: {args}")
    vPrint("-------------------------")
    
    user_agent = args.user_agent
    rbx_token = args.rbx_token

    env_file = args.env_file
    if env_file is not None:
        from modules import loadEnv
        if not os.path.isfile(env_file):
            loadEnv.createEnvTemplate(parser, env_file)
            print(".env file was successfully created! Use a text editor to edit")
            sys.exit(0)
        else:
            vPrint(f"Loading .env file [{args.env_file}]...")
            data = loadEnv.loadEnvFile(env_file)
            if rbx_token == None:
                rbx_token = data["rbx_token"]
            if user_agent == parser.get_default("user_agent"):
                user_agent = data["user_agent"]

    from modules import apiReqs, dataSave
    apiReqs.init(user_agent, rbx_token)

    user_id = args.user_id
    if user_id == parser.get_default("user_id") and apiReqs.isTokenCookieThere():
        userInfo = apiReqs.getUserFromToken()
        vPrint(f"userInfo: [{userInfo}]")
        user_id = userInfo["id"]
        #print(userInfo)

    data_folder = dataSave.get_data_file_path(args.cache_directory)
    if user_id != parser.get_default("user_id"):
        data_folder = os.path.join(data_folder,str(user_id))
    else:
        data_folder = os.path.join(data_folder,"guest")
    data_folder = dataSave.get_data_file_path(data_folder)

    if args.file_path == None:
        parser.error("the following arguments are required to continue: file_path")
    lines = [l.strip() for l in args.file_path.readlines()]
    args.file_path.close()
    # print(lines)

    vPrint("Starting scriptLoop...")
    from modules import scriptLoop
    scriptLoop.start(
        lines,
        user_id=user_id,
        awardedThreshold=args.awarded_threshold,
        secs_reincarnation=args.seconds,
        open_place_in_browser=args.open_in_browser,
        use_bloxstrap=args.no_bloxstrap,
        use_sober=args.no_sober,
        sober_opts=args.sober_opts,
        detectOneBadgeUniverses=args.detect_one_badge_games
        )

if __name__ == "__main__":
    main()