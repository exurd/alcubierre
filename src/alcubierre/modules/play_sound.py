# alcubierre
# ./modules/play_sound.py
"""
Plays sound for the program. Akin to verbosePrint.py,
the user can toggle it on/off, via toggle_sound(SndPack)
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import os
import sys
try:
    from playsound3 import playsound  # type: ignore
except ImportError:
    from playsound import playsound  # type: ignore

from alcubierre.modules.verbose_print import vPrint

ACTIVE_SND_PACK = None

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.join(os.path.dirname(__file__), "..")

sounds_folder = os.path.join(base_path, "sounds")
soundPacks = os.listdir(sounds_folder)
# print(sounds_folder)


def generate_sound_dict(folder):
    """
    Generates a dictionary from a folder with .wav files.
    """
    sound_dict = {}
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            sound_file = os.path.join(folder, file)
            sound_dict[file.replace(".wav", "")] = sound_file
    return sound_dict


class SndPack:
    """
    Sound Pack: folder with a bunch of sounds.
    Current sound names: error, notify, startup, success
    .wav files only! generate_sound_dict() only checks .wav files.
    """
    def __init__(self, theme: str = ""):
        if theme == "":
            return
        global ACTIVE_SND_PACK
        self.theme = theme
        self.folder = os.path.join(sounds_folder, theme)
        if os.path.exists(self.folder):
            self.sounds = generate_sound_dict(self.folder)
        else:
            self.sounds = {}
        ACTIVE_SND_PACK = self

    def __str__(self) -> str:
        return f"SndPack [folder: `{self.folder}`, sounds: `{self.sounds}`]"


def play_sound(sound_name: str):
    """
    Plays a sound in a Sound Pack that is named after the string.
    """
    if ACTIVE_SND_PACK:
        if sound_name in ACTIVE_SND_PACK.sounds:
            vPrint(f"Playing sound `{sound_name}`...")
            sound_file = ACTIVE_SND_PACK.sounds[sound_name]
            playsound(sound_file)


def toggle_sound(sound_pack: str):
    """
    Toggles sound on if a 'sound_pack' string is given.
    """
    global play_sound
    check = sound_pack is not None
    if check:
        SndPack(sound_pack)
    play_sound = play_sound if check else lambda *a, **k: None

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
