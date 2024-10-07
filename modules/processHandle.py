import os, subprocess, platform, time
import webbrowser

from . import apiReqs, dataSave
from .rbxTypes import rbxInstance, rbxReason, rbxType
from .verbosePrint import vPrint

CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008

# TODO: figure out system differences (this means that the script is windows only for now)
system = platform.system()

def process_exists(process_name):
    call = "TASKLIST", "/FI", "imagename eq %s" % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split("\r\n")[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def openRobloxPlace(rootPlaceId, bloxstrap=True, name=None):
    if name == None:
        print(f"Going to Roblox Place #{str(rootPlaceId)}")
    elif type(name) == str:
        print(f"Going to {str(name)} ({str(rootPlaceId)})")

    dataSave.played_places.append(rootPlaceId)
    dataSave.save_data(dataSave.played_places,"played_places.json")
    #if bloxstrap exists and on windows, use it (unless ignored by args)
    if system == "Windows" and bloxstrap:
        bs_path = f"{os.getenv("LOCALAPPDATA")}\\Bloxstrap"
        if os.path.exists(bs_path):
            # https://stackoverflow.com/questions/14797236/python-howto-launch-a-full-process-not-a-child-process-and-retrieve-the-pid
            # otherwise, quitting script also closes roblox
            process = subprocess.Popen([f"{bs_path}\\Bloxstrap.exe", f"roblox://experiences/start?placeId={rootPlaceId}"], creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
            vPrint(process)
            # return good or bad(...?)
    else:
        # TODO: test if this part of the script works after all these years

        # if not process_exists("RobloxPlayerBeta.exe"):
        #     print("Roblox is closed; re-opening it")
        #     webbrowser.open("roblox://")
        #     #time.sleep(10)

        final_url = "roblox://placeId=" + str(rootPlaceId)
        webbrowser.open(final_url)

def waitForProcessOrBadgeCollect(an_rbxInstance:rbxInstance,user_Id=0,secs_reincarnation=-1,singleBadge=True):
    """
    Wait for Roblox process to close or badge to be collected.
    """
    if secs_reincarnation == -1:
        print("Exit the game when you have finished.")
        while True:
            time.sleep(3)
            if not process_exists("RobloxPlayerBeta.exe"):
                return rbxReason.processClosed
            if an_rbxInstance.type == rbxType.BADGE and user_Id != 0:
                if singleBadge == True:
                    userBadge_check = apiReqs.checkUserInvForAsset(user_Id,an_rbxInstance.id)
                    if userBadge_check:
                        return rbxReason.badgeCollected
    else:
        print("You got " + str(secs_reincarnation) + " seconds")
        time.sleep(secs_reincarnation)
        return rbxReason.timeUp