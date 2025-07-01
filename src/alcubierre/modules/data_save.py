# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/data_save.py
"""
Handles data saving/loading.
Uses pickle (or pickle5 for older pythons) and json.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import os
import json
import pickle

from alcubierre.modules.verbose_print import vPrint

DATA_FOLDER = None

# variables to save
GOTTEN_BADGES = None
PLAYED_PLACES = None


def get_data_file_path(root_folder):
    """
    Sets DATA_FOLDER to a specifed root folder.
    """
    global DATA_FOLDER
    DATA_FOLDER = os.path.join(root_folder)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    vPrint(f"data_folder: [{DATA_FOLDER}]")
    return DATA_FOLDER


def load_data(filename, as_dict=False):
    """
    Load data from a file.
    The as_dict option will let you choose how to load the file,
    via pickle or json.
    """
    vPrint(f"Loading data from [{filename}]...")
    data_file_path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(data_file_path) and os.path.getsize(data_file_path) > 0:
        if as_dict:
            with open(data_file_path, "rb") as f:
                data = pickle.load(f)
                f.close()
        else:
            with open(data_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                f.close()
    else:
        if as_dict:
            data = {}
        else:
            data = []
    return data


def save_data(data, filename):
    """
    Save data to a file.
    If the data is a dictionary, it will save as a Pickle Protocol 5 file.
    Else, it will dump as a sorted key JSON with 4 space indent.
    """
    vPrint(f"Saving data to [{filename}]...")
    data_file_path = os.path.join(DATA_FOLDER, filename)
    if isinstance(data, dict):
        with open(data_file_path, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
    else:
        with open(data_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, sort_keys=True)
            f.close()


def init():
    """
    Initialises variables from json files.
    """
    global GOTTEN_BADGES
    global PLAYED_PLACES
    GOTTEN_BADGES = load_data("gotten_badges.json")
    PLAYED_PLACES = load_data("played_places.json")

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
