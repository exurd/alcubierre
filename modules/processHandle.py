import os, subprocess, platform, time, psutil
import webbrowser

from . import apiReqs, dataSave
from .rbxTypes import rbxInstance, rbxReason, rbxType
from .verbosePrint import vPrint

CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008

FLATPAK_SOBER_OPTS = "run --branch=master --arch=x86_64 --command=sober --file-forwarding org.vinegarhq.Sober"

# TODO: figure out system differences (this means that the script is windows and linux only for now)
SYSTEM = platform.system()
vPrint(f"System: {SYSTEM}")

if SYSTEM == "Windows":
    robloxProcess_name = "RobloxPlayerBeta.exe"
elif SYSTEM == "Linux":
    robloxProcess_name = "sober"

# https://stackoverflow.com/a/62823656
def linux_process_exists(process_name):
    try:
        call = subprocess.check_output("pidof '{}'".format(process_name), shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

# https://stackoverflow.com/a/29275361
def win_process_exists(process_name) -> bool:
    call = "TASKLIST", "/FI", "imagename eq %s" % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split("\r\n")[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def kill_process():
    print("Closing Roblox in 5 seconds...")
    time.sleep(5)
    vPrint(f"Killing in the name of `{robloxProcess_name}`")
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == robloxProcess_name:
            proc.kill()
            vPrint(f"Killed process with PID {proc.pid}")

def openRobloxPlace(rootPlaceId, name=None, use_bloxstrap=True, use_sober=True, sober_opts=""):
    if name == None:
        print(f"Going to Roblox Place #{str(rootPlaceId)}")
    elif type(name) == str:
        print(f"Going to {str(name)} ({str(rootPlaceId)})")

    dataSave.played_places.append(rootPlaceId)
    dataSave.save_data(dataSave.played_places,"played_places.json")
    #if bloxstrap exists and on windows, use it (unless ignored by args)
    if SYSTEM == "Windows" and use_bloxstrap:
        bs_path = f"{os.getenv('LOCALAPPDATA')}\\Bloxstrap"
        if os.path.exists(bs_path):
            # https://stackoverflow.com/questions/14797236/python-howto-launch-a-full-process-not-a-child-process-and-retrieve-the-pid
            # otherwise, quitting script also closes roblox
            process = subprocess.Popen([f"{bs_path}\\Bloxstrap.exe", f"roblox://experiences/start?placeId={rootPlaceId}"], creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
            vPrint(process)
            # return good or bad(...?)
    elif SYSTEM == "Linux" and use_sober:
        sober_path = os.path.join(os.path.expanduser("~"), ".var/app/org.vinegarhq.Sober")
        if os.path.exists(sober_path):
            if sober_opts != "":
                sober_command = ["flatpak"] + FLATPAK_SOBER_OPTS.split() + sober_opts.split() + [f"roblox://experiences/start?placeId={rootPlaceId}"]
            else:
                sober_command = ["flatpak"] + FLATPAK_SOBER_OPTS.split() + [f"roblox://experiences/start?placeId={rootPlaceId}"]
            process = subprocess.Popen(sober_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            vPrint(process)
    else: # fallback that might or might not work *shrug*
        # TODO: test if this part of the script works after all these years

        # if not process_exists("RobloxPlayerBeta.exe"):
        #     print("Roblox is closed; re-opening it")
        #     webbrowser.open("roblox://")
        #     #time.sleep(10)

        final_url = "roblox://placeId=" + str(rootPlaceId)
        webbrowser.open(final_url)

def openPlaceInBrowser(placeId):
    url = "https://www.roblox.com/games/" + str(placeId)
    vPrint(f"Opening {url}")
    webbrowser.open(url)

def waitForProcessOrBadgeCollect(an_rbxInstance:rbxInstance,user_Id=0,secs_reincarnation=-1,singleBadge=True) -> rbxReason:
    """
    Wait for Roblox process to close or badge to be collected.
    """
    if secs_reincarnation == -1:
        print("Exit the game when you have finished.")
        while True:
            time.sleep(3)
            if SYSTEM == "Windows":
                if not win_process_exists("RobloxPlayerBeta.exe"):
                    return rbxReason.processClosed
            if SYSTEM == "Linux":
                if not linux_process_exists("sober"):
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