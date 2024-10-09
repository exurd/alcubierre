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