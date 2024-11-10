# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/processHandle.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

import os, subprocess, platform, time, psutil
import webbrowser

from . import apiReqs, dataSave
from .rbxTypes import rbxInstance, rbxReason, rbxType
from .verbosePrint import vPrint

CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008

FLATPAK_SOBER_OPTS = "run --branch=master --arch=x86_64 --command=sober --file-forwarding org.vinegarhq.Sober"

SYSTEM = platform.system()
vPrint(f"System: {SYSTEM}")

if SYSTEM == "Windows":
    robloxProcess_name = "RobloxPlayerBeta.exe"
elif SYSTEM == "Linux":
    robloxProcess_name = "sober"
if SYSTEM == "Darwin":
    robloxProcess_name = "RobloxPlayer"

def roblox_process_exists() -> psutil.Process:
    for proc in psutil.process_iter():
        try:
            if proc.name() == robloxProcess_name: return proc
        except psutil.NoSuchProcess: pass
    return None

def kill_roblox_process():
    print("Closing Roblox in 5 seconds...")
    time.sleep(5)
    vPrint(f"Killing in the name of `{robloxProcess_name}`")
    proc = roblox_process_exists()
    if type(proc) == psutil.Process:
        proc.kill()
        vPrint(f"Killed process with PID {proc.pid}")

def openRobloxPlace(rootPlaceId, name=None, use_bloxstrap=True, use_sober=True, sober_opts=""):
    if name == None:
        print(f"Going to Roblox Place #{str(rootPlaceId)}")
    elif type(name) == str:
        print(f"Going to {str(name)} ({str(rootPlaceId)})")

    dataSave.played_places.append(rootPlaceId)
    dataSave.save_data(dataSave.played_places,"played_places.json")

    roblox_uri = f"roblox://experiences/start?placeId={str(rootPlaceId)}"

    #if bloxstrap exists and on windows, use it (unless ignored by args)
    if SYSTEM == "Windows" and use_bloxstrap:
        bs_path = f"{os.getenv('LOCALAPPDATA')}\\Bloxstrap"
        if os.path.exists(bs_path):
            # https://stackoverflow.com/questions/14797236/python-howto-launch-a-full-process-not-a-child-process-and-retrieve-the-pid
            # otherwise, quitting script also closes roblox
            process = subprocess.Popen([f"{bs_path}\\Bloxstrap.exe", "-player", roblox_uri], creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
            vPrint(process)
            # return good or bad(...?)
    elif SYSTEM == "Linux" and use_sober:
        sober_path = os.path.join(os.path.expanduser("~"), ".var/app/org.vinegarhq.Sober")
        if os.path.exists(sober_path):
            sober_command = ["flatpak"] + FLATPAK_SOBER_OPTS.split()
            if sober_opts != "":
                sober_command += sober_opts.split() + [roblox_uri]
            else:
                sober_command += [roblox_uri]
            vPrint(f"sober_command: [{sober_command}]")
            process = subprocess.Popen(sober_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            vPrint(process)
    else: # fallback that might or might not work *shrug*
        # TODO: test if this part of the script works after all these years

        # if not process_exists("RobloxPlayerBeta.exe"):
        #     print("Roblox is closed; re-opening it")
        #     webbrowser.open("roblox://")
        #     #time.sleep(10)

        webbrowser.open(roblox_uri)

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
            if not type(roblox_process_exists()) == psutil.Process:
                return rbxReason.processClosed
            if an_rbxInstance.type == rbxType.BADGE and user_Id != 0:
                if singleBadge == True:
                    userBadge_check = apiReqs.checkUserInvForBadge(user_Id,an_rbxInstance.id)
                    if userBadge_check:
                        return rbxReason.badgeCollected
                    time.sleep(7) # 10 secs to avoid rate limiting
    else:
        print("You got " + str(secs_reincarnation) + " seconds")
        time.sleep(secs_reincarnation)
        return rbxReason.timeUp

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