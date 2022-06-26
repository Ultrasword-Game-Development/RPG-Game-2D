"""
Contains functions and methods for serializing level data

Serializable objects:
- Rect
- Animation
- Entity
- Chunk
- World
- Handler
- State

Output will be a .json file
Data can be loaded using the classes made in this file

"""

import json
import pickle

from engine.globals import *


# TODO - make a global image section for the json
# all the images will be stored there



# ------- Serialize base object -------- #


def save_to_file(file_path: str, data: dict) -> None:
    """Saves data to a .json file"""
    if not file_path.endswith(".json"):
        file_path += ".json"
    with open(file_path, "w") as file:
        json.dump(data, file) # indent=4)
        file.close()


def load_json_data(file_path: str) -> dict:
    """Open file and load as a json"""
    with open(file_path, 'r') as file:
        data = json.load(file)
        file.close()
    return data
