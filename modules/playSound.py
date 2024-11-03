# alcubierre
# ./modules/playSound.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "CONTRIBUTE TO PYGAME!! https://www.pygame.org/wiki/Contribute"
import pygame
import time

from .verbosePrint import vPrint

active_sndPack = None

sounds_folder = os.path.join(".","sounds")
soundPacks = os.listdir(sounds_folder)
# print(sounds_folder)

def genSoundDict(folder):
    soundDict = {}
    for file in os.listdir(folder):
        if file.endswith(".ogg"):
            sound_file = os.path.join(folder, file)
            soundDict[file.replace(".ogg","")] = sound_file
    return soundDict

class sndPack:
    def __init__(self,theme:str=None):
        global active_sndPack
        self.theme = theme
        self.folder = os.path.join(sounds_folder,theme)
        if os.path.exists(self.folder):
            self.sounds = genSoundDict(self.folder)
        else:
            self.sounds = {}
        active_sndPack = self
    
    def __str__(self) -> str:
        return f"sndPack [folder: `{self.folder}`, sounds: `{self.sounds}`]"

def playSound(soundName:str):
    global active_sndPack
    if pygame.mixer.get_init() and active_sndPack:
        if soundName in active_sndPack.sounds:
            vPrint(f"Playing sound `{soundName}`...")
            soundFile = active_sndPack.sounds[soundName]
            snd = pygame.mixer.Sound(soundFile)
            channel = snd.play()
            while channel.get_busy():
                pygame.time.delay(100)

def toggleSoundWithSoundPack(soundPack):
    global playSound
    if soundPack != None:
        pygame.mixer.init()
        sndPack(soundPack)

    playSound = playSound if soundPack != None else lambda *a, **k: None

def fadeAllSounds(milliSecs=1000):
    if pygame.mixer.get_init():
        pygame.mixer.fadeout(milliSecs)
        time.sleep((milliSecs/1000))

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