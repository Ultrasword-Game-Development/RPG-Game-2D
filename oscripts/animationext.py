import pygame
import os
import json

from engine.graphics import animation
from engine.misc import maths
from engine.handler.filehandler import Filehandler

from . import singleton


# -------------------------------------------------- #
# image handling functions

def handle_handle_position(framedata):
    """Find and remove the handle positions"""
    pos = (0, 0)
    f = False
    for x in range(framedata.sprite_source_location.w):
        for y in range(framedata.sprite_source_location.h):
            if framedata.oframe.get_at((x, y)) == singleton.HANDLE_POS_COL:
                f = True
                framedata.oframe.set_at((x, y), (0, 0, 0, 0))
                pos = (x, y)
                break
        if f:
            break
    framedata.points[singleton.HANDLE_IDENTIFIER] = pos


def rect_to_dict(rect):
    return {'x': rect.x, 'y': rect.y, 'w': rect.w, 'h': rect.h}


def rot_rect_90deg(rect, orect):
    """Rounds the rect 90 deg - counterclockwise"""
    result = pygame.Rect(0, 0, 0, 0)
    # newly rotate point
    result.x = rect.y
    result.y = orect.w - rect.right
    result.w = rect.h
    result.h = rect.w
    return result


# -------------------------------------------------- #
# load and parse animations with rotations
def load_and_parse_aseprite_animation_wrotations(filepath, rotations, rot_range=(0, 360)):
    """
    Load and parse and aseprite animatino with rotations!

    !!!! WARNING !!!!!
    Susceptible to Multiple loads!
    Use with care...
    Use with this in mind!
    """
    # load file
    with open(filepath, 'r') as file:
        filedata = json.load(file)
        file.close()
    metadata = filedata["meta"]
    framedata = filedata["frames"]
    parsedframedata = animation.parse_frame_data(framedata)
    # load animations with rotations
    image = metadata['image']
    for category in parsedframedata:
        result = animation.Category(category, {}, parsedframedata)
        for ani in parsedframedata[category]:
            result.anims[ani] = RotatedAnimationDataSet(ani, Filehandler.get_image(
                os.path.join(os.path.dirname(filepath), image)), parsedframedata[category][ani], result, rotations,
                                                        rot_range)
            result.anims[ani].hitbox_analysis()
            result.anims[ani].create_rotated_frames()
        animation.Category.CATEGORIES[category] = result
    # -------------------------------------------------- #
    # return info
    info = {"file": filepath, "cat": list(parsedframedata.keys()), "rotations": rotations, "range": rot_range, "layers": metadata["layers"]}
    return info


# -------------------------------------------------- #
# rotated registry

class RotatedRegistry(animation.Registry):
    def __init__(self, parent):
        super().__init__(parent)
        self.angle = 0
        self.index_offset = self.calc_index_offset() * self.parent.length

    def calc_index_offset(self):
        return round((self.angle if self.angle > 0 else 360 + self.angle) / self.parent.rot_angle) % self.parent.rot_angle % self.parent.rotations

    def update_angle(self):
        self.index_offset = self.calc_index_offset() * self.parent.length

    def get_frame(self):
        return self.parent.frames[self.index_offset + self.fnum].frame


class RotatedAnimationDataSet(animation.AnimationDataSet):
    def __init__(self, name, sprite, frames, parent, rotations, rot_range=(0, 360)):
        super().__init__(name, sprite, frames, parent)
        self.rotations = rotations
        self.rot_angle = (rot_range[1] - rot_range[0]) // self.rotations  # TODO - finalize this??
        # set up the rotated frames

    def create_rotated_frames(self):
        for rot in range(1, self.rotations):
            for f in range(self.length):
                result = animation.FrameData(f, True, False, self.frames[f].source_size,
                                             rect_to_dict(self.frames[f].sprite_source_location),
                                             self.frames[f].duration)
                result.oframe = pygame.transform.rotate(self.frames[f].oframe, rot * self.rot_angle)
                result.frame = result.oframe
                # rotate hitbox
                hbox = self.frames[f].hitbox
                for i in range(int(rot * self.rot_angle / 90) % 4):
                    hbox = rot_rect_90deg(hbox, self.frames[f].ohitbox)
                result.hitbox = hbox
                self.frames.append(result)

    def get_registry(self):
        return RotatedRegistry(self)
