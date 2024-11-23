# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/processHandle.py
"""
Loads enviroment file.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import os
import subprocess
import platform
import time
import webbrowser
import psutil

from modules import apiReqs, dataSave
from modules.rbxTypes import RbxInstance, RbxReason, RbxType
from modules.verbosePrint import vPrint

CREATE_NEW_PROCESS_GROUP = 0x00000200
DETACHED_PROCESS = 0x00000008

FLATPAK_SOBER_OPTS = "run --branch=master --arch=x86_64 --command=sober --file-forwarding org.vinegarhq.Sober"

SYSTEM = platform.system()
vPrint(f"System: {SYSTEM}")

ROBLOX_PROCESS_NAME = ""
if SYSTEM == "Windows":
    ROBLOX_PROCESS_NAME = "RobloxPlayerBeta.exe"
elif SYSTEM == "Linux":
    ROBLOX_PROCESS_NAME = "sober"
if SYSTEM == "Darwin":
    ROBLOX_PROCESS_NAME = "RobloxPlayer"


def roblox_process_exists() -> psutil.Process:
    """
    Checks if the Roblox process exists.
    Uses psutil to detect the name
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == ROBLOX_PROCESS_NAME:
                return proc
        except psutil.NoSuchProcess:
            pass
    return None


def kill_roblox_process():
    """
    Kills the Roblox process.
    To allow the user to react, a 5 second delay is given before closing.
    """
    print("Closing Roblox in 5 seconds...")
    time.sleep(5)
    vPrint(f"Killing in the name of `{ROBLOX_PROCESS_NAME}`")
    proc = roblox_process_exists()
    if isinstance(proc, psutil.Process):
        proc.kill()
        vPrint(f"Killed process with PID {proc.pid}")


def open_roblox_place(root_place_id, name=None, use_bloxstrap=True, use_sober=True, sober_opts=""):
    """
    Opens a Roblox place.
    `name` prints alongside the 'going to' message.
    `use_bloxstrap` uses Bloxstrap if available.
    `use_sober` uses Sober if available.
    `sober_opts` sets the options for Sober.
    """
    if name is None:
        print(f"Going to Roblox Place #{str(root_place_id)}")
    elif isinstance(name, str):
        print(f"Going to {str(name)} ({str(root_place_id)})")

    dataSave.PLAYED_PLACES.append(root_place_id)
    dataSave.save_data(dataSave.PLAYED_PLACES, "played_places.json")

    roblox_uri = f"roblox://experiences/start?placeId={str(root_place_id)}"

    # if bloxstrap exists and on windows, use it (unless ignored by args)
    if SYSTEM == "Windows" and use_bloxstrap:
        bs_path = f"{os.getenv('LOCALAPPDATA')}\\Bloxstrap"
        if os.path.exists(bs_path):
            # https://stackoverflow.com/questions/14797236/python-howto-launch-a-full-process-not-a-child-process-and-retrieve-the-pid
            # otherwise, quitting script also closes roblox
            process = subprocess.Popen(
                [f"{bs_path}\\Bloxstrap.exe", "-player", roblox_uri],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
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
            process = subprocess.Popen(sober_command,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.STDOUT)
            vPrint(process)
    else:  # fallback that might or might not work *shrug*
        # TODO: test if this part of the script works after all these years

        # if not process_exists("RobloxPlayerBeta.exe"):
        #     print("Roblox is closed; re-opening it")
        #     webbrowser.open("roblox://")
        #     #time.sleep(10)

        webbrowser.open(roblox_uri)


def open_place_in_browser(place_id):
    """
    Uses webbrowser to open the webpage for the game in the default browser.
    """
    url = "https://www.roblox.com/games/" + str(place_id)
    vPrint(f"Opening {url}")
    webbrowser.open(url)


def wait_for_process_or_badge_collect(a_rbx_instance: RbxInstance, user_id=0, secs_reincarnation=-1, single_badge=True) -> RbxReason:
    """
    Wait for Roblox process to close or badge to be collected.
    """
    if secs_reincarnation == -1:
        print("Exit the game when you have finished.")
        while True:
            time.sleep(3)
            if not isinstance(roblox_process_exists(), psutil.Process):
                return RbxReason.PROCESS_CLOSED
            if a_rbx_instance.type == RbxType.BADGE and user_id != 0:
                if single_badge:
                    user_badge_check = apiReqs.check_user_inv_for_badge(user_id, a_rbx_instance.id)
                    if user_badge_check:
                        return RbxReason.BADGE_COLLECTED
                    time.sleep(7)  # 10 secs to avoid rate limiting
    else:
        print("You got " + str(secs_reincarnation) + " seconds")
        time.sleep(secs_reincarnation)
        return RbxReason.TIME_UP

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
