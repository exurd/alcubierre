# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/dataSave.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

import os
import json

from .verbosePrint import vPrint

data_folder = None

# variables to save
gotten_badges = None
played_places = None

def get_data_file_path(rootFold):
    global data_folder
    data_folder = os.path.join(rootFold)
    os.makedirs(data_folder, exist_ok=True)
    vPrint(f"data_folder: [{data_folder}]")
    return data_folder

def load_data(filename):
    vPrint(f"Loading data from [{filename}]...")
    global data_folder
    data_file_path = os.path.join(data_folder, filename)
    if os.path.exists(data_file_path) and os.path.getsize(data_file_path) > 0:
        with open(data_file_path, "r") as f:
            data = json.load(f)
            f.close()
    else:
        data = []
    return data

def save_data(data, filename):
    vPrint(f"Saving data to [{filename}]...")
    global data_folder
    data_file_path = os.path.join(data_folder, filename)
    with open(data_file_path, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.close()

def init():
    global gotten_badges
    global played_places
    gotten_badges = load_data("gotten_badges.json")
    played_places = load_data("played_places.json")

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.