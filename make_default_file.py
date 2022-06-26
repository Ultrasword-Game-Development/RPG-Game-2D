import os


default = """import pygame\n
import engine
from engine import window, clock, user_input, handler, draw
from engine import filehandler, maths, animation, state, serialize
from engine import spritesheet, core_utils
from engine.globals import *\n\n\n"""

path = input("Input the relative path: ")

if not path.endswith('.py'):
    path += ".py"

with open(path, 'w') as file:
    file.write(default)
    file.close()

print("Finished writing!")
