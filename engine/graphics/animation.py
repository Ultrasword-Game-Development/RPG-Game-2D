import json
import os
import pygame

from ..singleton import *
from ..handler.filehandler import Filehandler
from ..handler.eventhandler import Eventhandler
from ..misc import clock


# -------------------------------------------------- #
# registry

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
        - fini                  = int (# times it loops)
        """
        self.parent = parent
        self.fnum = 0
        self.tpass = 0.0
        self.fini = 0

    def update(self):
        self.tpass += clock.delta_time
        if self.tpass >= self.parent.frames[self.fnum].duration:
            self.tpass = 0.0
            self.fnum += 1
            if self.fnum >= self.parent.length:
                self.fnum = 0
                self.fini += 1

    def has_finished(self):
        if self.fini:
            self.fini = 0
            return True
        return False

    def get_frame(self):
        """Get the frame"""
        return self.parent.frames[self.fnum].frame

    def get_frame_data(self):
        """Get the frame data"""
        return self.parent.frames[self.fnum]

    def change_dataset(self, new: str):
        """Change the animation data set"""
        if new in self.parent.parent.anims:
            self.parent = self.parent.parent.anims[new]
            self.fnum = 0
            self.tpass = 0.0
            self.changed = True

    def get_hitbox(self):
        """Get hitbox at a certain frame"""
        return self.parent.frames[self.fnum].hitbox


# -------------------------------------------------- #
# framedata

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
        - origin frame image        = pygame.Surface
        - the frame image           = pygame.Surface
        """
        self.parent = None
        self.frame_number = 0
        self.source_size = s_size
        self.sprite_source_location = pygame.Rect(s_s_loc['x'], s_s_loc['y'], s_s_loc['w'], s_s_loc['h'])
        self.duration = dur
        self.rotated = rot
        self.trimmed = trim
        self.points = {}

        # get the frame
        self.oframe = None
        self.frame = None
        self.ohitbox = pygame.Rect(0, 0, s_size['w'], s_size['h'])
        self.hitbox = pygame.Rect(0, 0, s_size['w'], s_size['h'])
        self.scale = 1

    def get_sprite(self):
        """After loading data + parsing aseprite | call this to get the image"""
        self.oframe = self.parent.sprite.subsurface(self.sprite_source_location)
        self.frame = self.oframe

    def rescale_sprite(self, scale):
        """Resize a sprite based off scale"""
        self.scale = scale
        self.frame = pygame.transform.scale(self.oframe, (
            int(self.oframe.get_size()[0] * scale), int(self.oframe.get_size()[1] * scale)))
        self.update_hitbox()

    def set_hitbox(self, new):
        """Set the hitbox to new hitbox"""
        self.ohitbox = new
        self.update_hitbox()

    def update_hitbox(self):
        ls, ts = self.ohitbox.x / self.sprite_source_location.w, self.ohitbox.y / self.sprite_source_location.h
        rs, bs = self.ohitbox.right / self.sprite_source_location.w, self.ohitbox.bottom / self.sprite_source_location.h
        # print(ls, ts, rs, bs)

        newsize = self.oframe.get_size()
        self.hitbox.x = int(ls * newsize[0] * self.scale)
        self.hitbox.y = int(ts * newsize[1] * self.scale)
        self.hitbox.w = int((rs - ls) * newsize[0] * self.scale)
        self.hitbox.h = int((bs - ts) * newsize[1] * self.scale)

    def get_point(self, point: str):
        """Get a point given the identifier"""
        return self.points[point]

    def __str__(self):
        return f"{self.frame_number}-{self.source_size}"

    @staticmethod
    def __sort__(x):
        return x.frame_number


# -------------------------------------------------- #
# data set

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

    def hitbox_analysis(self):
        """Perform hitbox analysis"""
        # print(self.name)
        for f in self.frames:
            f.set_hitbox(find_and_remove_image_hitbox(f.frame))

    def rescale_images(self, scale: float):
        """Resize all sprite images"""
        for fd in self.frames:
            fd.rescale_sprite(scale)

    def get_framedata(self, index):
        """Get a framedata object at a specific index"""
        return self.frames[index]

    def get_frame_dimensions(self, index):
        """get the sprite dimensions"""
        return self.frames[index].frame.get_size()

    def get_frame_count(self):
        """Get the amount of frames"""
        return self.length

    def apply_func_to_frames(self, _func):
        """Apply a given function to each framedata object"""
        for x in self.frames:
            _func(x)


# -------------------------------------------------- #
# category

class Category:
    CATEGORIES = {}
    LOADED_JSONS = {}

    @classmethod
    def get_category(cls, name):
        return Category.CATEGORIES.get(name)

    def __init__(self, name: str, related_animations: dict, raw_data: dict):
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
        self.raw_data = raw_data

    def get_animation(self, name):
        """Get an animation"""
        return self.anims[name]

    def rescale_all_animation(self, scale):
        """Rescale all animation"""
        for aname, anim in self.anims.items():
            anim.rescale_images(scale)

    def create_registry_for_all(self):
        """Creates a dict of registries to be used"""
        return {ani.name: ani.get_registry() for ani in self.anims.values()}

    def apply_func_to_animations(self, _func):
        """Apply a functino to all animations"""
        for x in self.anims.values():
            x.apply_func_to_frames(_func)


# -------------------------------------------------- #
# functions

def load_and_parse_aseprite_animation(filepath) -> dict:
    """Loads and parses an asesprite animation"""
    # don't load things twice
    if filepath in Category.LOADED_JSONS:
        return {"file": filepath, "cat": list(Category.get_category(filepath))}
    # get data
    with open(filepath, 'r') as file:
        filedata = json.load(file)
        file.close()
    # loaded data - now parse data
    metadata = filedata["meta"]
    framedata = filedata["frames"]
    # prase frame data
    parsedframedata = parse_frame_data(framedata)
    # create AnimationDataSet and Category Objects
    load_categories(metadata, filepath, parsedframedata)

    # add important info to buffer -- get first animation bc aseprite only holds one cat
    Category.LOADED_JSONS[filepath] = list(parsedframedata.keys())[0]

    # important info
    info = {"file": filepath, "cat": list(parsedframedata.keys()), "meta": metadata}
    return info


def load_categories(metadata, filepath, parsedframedata):
    """Given parsed frame data, all the animations are created and cached"""
    image = metadata['image']
    for category in parsedframedata:
        # create object
        result = Category(category, {}, parsedframedata)
        # for every animation (layer) in aseprite -- create a dataset
        for animation in parsedframedata[category]:
            result.anims[animation] = AnimationDataSet(animation, Filehandler.get_image(
                os.path.join(os.path.dirname(filepath), image)), parsedframedata[category][animation], result)
            result.anims[animation].hitbox_analysis()
        Category.CATEGORIES[category] = result


def parse_frame_data(framedata) -> dict:
    """Parse aseprite framedata into dict"""
    result = {}
    for f in framedata:
        fname = f["filename"].split('-')
        category_name = fname[0]
        ani_name = fname[1]
        f_num = int(fname[2].split('.')[0])
        frame = FrameData(f_num, f["rotated"], f["trimmed"], f["sourceSize"], f["frame"], f["duration"] / 1000)
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


def find_and_remove_image_hitbox(image):
    """Find hitboxes on an image given hitbox color"""
    size = image.get_size()
    result = pygame.Rect(0, 0, size[0], size[1])
    hfx = size[0] // 2
    hfy = size[1] // 2
    # look for left hitbox
    done = False
    for x in range(hfx):
        for y in range(size[1]):
            if image.get_at((x, y)) == HORIZONTAL_HITBOX_COL:
                result.x = x + 1
                image.set_at((x, y), (0, 0, 0, 0))
                done = True
                break
        if done:
            break
    if not done:
        result.x = 0
    # look for right
    done = False
    for x in range(size[0] - 1, hfx - 1, -1):
        for y in range(size[1]):
            if image.get_at((x, y)) == HORIZONTAL_HITBOX_COL:
                result.w = x - result.x
                image.set_at((x, y), (0, 0, 0, 0))
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
            if image.get_at((x, y)) == VERTICAL_HITBOX_COL:
                result.y = y + 1
                image.set_at((x, y), (0, 0, 0, 0))
                done = True
                break
        if done:
            break
    if not done:
        result.y = 0
    # look for bottom
    done = False
    for x in range(size[0]):
        for y in range(size[1] - 1, hfy - 1, -1):
            if image.get_at((x, y)) == VERTICAL_HITBOX_COL:
                result.h = y - result.y
                image.set_at((x, y), (0, 0, 0, 0))
                done = True
                break
        if done:
            break
    if not done:
        result.h = size[1] - result.y
    return result
