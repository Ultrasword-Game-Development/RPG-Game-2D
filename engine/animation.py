import json
import os
import pygame

from .globals import *
from .filehandler import Filehandler
from . import clock


class Registry:
    """
    Registry allos different objects to access animation frames
    - maintains the fps of an animation
    """
    def __init__(self, parent):
        """
        Constructor for Registry
        - parent                = AnimationDataSet
        - fnum                  = int
        - tpass                 = float
        """
        self.parent = parent
        self.fnum = 0
        self.tpass = 0.0
        self.changed = True

    def update(self):
        self.tpass += clock.delta_time
        if self.tpass >= self.parent.frames[self.fnum].duration:
            self.tpass = 0.0
            self.fnum += 1
            if self.fnum >= self.parent.length:
                self.fnum = 0

    def get_frame(self):
        """Get the frame"""
        return self.parent.frames[self.fnum].frame



class FrameData:
    """
    FrameData contains data for a frame
    - all frames should be loaded from an asesprite exported spritesheet
    """
    def __init__(self, f_num: int, rot: bool, trim: bool, s_size, s_s_loc, dur):
        """
        Constructor for FrameData
        contains:
        - parent                    = AnimationDataSet
        - frame_number              = frame_number int
        - rotated                   = rotated bool
        - trimmed                   = trimmed bool
        - source_size               = source_size [int, int]
        - sprite_source_location    = sprite_source_location [int, int, int,int]
        - duration                  = duraction

        Loaded after creation
        - the frame image           = frame
        """
        self.parent = None
        self.frame_number = 0
        self.source_size = s_size
        self.sprite_source_location = pygame.Rect(s_s_loc['x'], s_s_loc['y'], s_s_loc['w'], s_s_loc['h'])
        self.duration = dur
        self.rotated = rot
        self.trimmed = trim

        # get the frame
        self.frame = None
    
    def get_sprite(self):
        """After loading data + parsing aseprite | call this to get the image"""
        self.frame = self.parent.sprite.subsurface(self.sprite_source_location)

    def __str__(self):
        return f"{self.frame_number}-{self.source_size}"
    
    @staticmethod
    def __sort__(x):
        return x.frame_number


class AnimationDataSet:
    def __init__(self, name, sprite, frames, parent):
        """
        Constructor for AnimationDataSet
        contains:
        - animation_name
        - animation_frames

        file_data is parsed : aseprite data format [not hashed / use array format]
        """
        self.name = name
        self.sprite = sprite
        self.frames = frames
        self.length = len(frames)
        self.parent = parent
        for f in self.frames:
            f.parent = self
            f.get_sprite()
    
    def get_registry(self):
        """Get a registry to access frames"""
        return Registry(self)

class Category:
    CATEGORIES = {}

    @classmethod
    def get_category(cls, name):
        return Category.CATEGORIES.get(name)

    def __init__(self, name: str, related_animations: dict):
        """
        An animation category
        contains:
        - related_animations

        Groups related animations together
        - for example, a player may have run, idle, etc animations
        Category = player, and an array would be held
        """
        self.name = name
        self.anims = related_animations

    def get_animation(self, name):
        """Get an animation"""
        return self.anims[name]


def load_and_parse_aseprite_animation(filepath):
    """Loads and parses an asesprite animation"""
    with open(filepath, 'r') as file:
        filedata = json.load(file)
        file.close()
    # loaded data - now parse data
    metadata = filedata["meta"]
    framedata = filedata["frames"]
    # get relavant metadata
    image = metadata["image"]
    # prase frame data
    parsedframedata = parse_frame_data(framedata)
    # create AnimationDataSet and Category Objects
    for category in parsedframedata:
        result = Category(category, {})
        for animation in parsedframedata[category]:
            result.anims[animation] = AnimationDataSet(animation, Filehandler.get_image(os.path.join(os.path.dirname(filepath), image)), parsedframedata[category][animation], result)
        Category.CATEGORIES[category] = result

def parse_frame_data(framedata) -> dict:
    """Parse aseprite framedata into dict"""
    result = {}
    for f in framedata:
        fname = f["filename"].split('-')
        category_name = fname[0]
        ani_name = fname[1]
        f_num = int(fname[2].split('.')[0])
        frame = FrameData(f_num, f["rotated"], f["trimmed"], f["sourceSize"], f["frame"], f["duration"]/1000)
        if category_name not in result:
            result[category_name] = {}
        # input data into the category
        if ani_name not in result[category_name]:
            result[category_name][ani_name] = []
        result[category_name][ani_name].append(frame)
    for cat in result:
        for ani in result[cat]:
            result[cat][ani].sort(key=FrameData.__sort__)
    return result

def find_image_hitbox(image):
    """Find hitboxes on an image given hitbox color"""
    size = image.get_size()
    result = pygame.Rect(0, 0, size[0], size[1])
    hfx = size[0]//2
    hfy = size[1]//2
    # look for left hitbox
    done = False
    for x in range(hfx):
        for y in range(size[1]):
            if image.get_at((x,y)) == HORIZONTAL_HITBOX_COL:
                result.x = x+1
                done = True
                break
        if done:
            break
    if not done:
        result.x = 0
    # look for right
    done = False
    for x in range(size[0]-1, hfx-1, -1):
        for y in range(size[1]):
            if image.get_at((x,y)) == HORIZONTAL_HITBOX_COL:
                result.w = x-result.x
                done = True
                break
        if done:
            break
    if not done:
        result.w = size[0] - result.x
    # look for top
    done = False
    for x in range(size[0]):
        for y in range(hfy):
            if image.get_at((x,y)) == VERTICAL_HITBOX_COL:
                result.y = y+1
                done = True
                break
        if done:
            break
    if not done:
        result.y = 0
    # look for bottom
    done = False
    for x in range(size[0]):
        for y in range(size[1]-1, hfy-1, -1):
            if image.get_at((x,y)) == VERTICAL_HITBOX_COL:
                result.h = y - result.y
                done = True
                break
        if done:
            break
    if not done:
        result.h = size[1] - result.y
    print(result)
    return result




