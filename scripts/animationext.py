import pygame
import os
import json

from engine import animation, maths
from engine.filehandler import Filehandler



# ------- functions ---------- #

def rect_to_dict(rect):
    return {'x':rect.x,'y':rect.y,'w':rect.w,'h':rect.h}


def rot_rect_90deg(rect, orect):
    """Rounds the rect 90 deg - counterclockwise"""
    result = pygame.Rect(0, 0, 0, 0)
    # newly rotate point
    result.x = rect.y
    result.y = orect.w-rect.right
    result.w = rect.h
    result.h = rect.w
    return result


def load_and_parse_aseprite_animation_wrotations(filepath, rotations):
    with open(filepath, 'r') as file:
        filedata = json.load(file)
        file.close()
    metadata = filedata["meta"]
    framedata = filedata["frames"]
    parsedframedata = animation.parse_frame_data(framedata)
    # load animations with rotations
    image = metadata['image']
    for category in parsedframedata:
        result = animation.Category(category, {})
        for ani in parsedframedata[category]:
            result.anims[ani] = RotatedAnimationDataSet(ani, Filehandler.get_image(os.path.join(os.path.dirname(filepath), image)), parsedframedata[category][ani], result, rotations)
            result.anims[ani].hitbox_analysis()
            result.anims[ani].create_rotated_frames()
        animation.Category.CATEGORIES[category] = result


# --------- classes ----------- #

class RotatedRegistry(animation.Registry):
    def __init__(self, parent):
        super().__init__(parent)
        self.angle = 0
        self.index_offset = self.calc_index_offset() * self.parent.length

    def calc_index_offset(self):
        return round(self.angle / self.parent.rot_angle) % self.parent.rot_angle % self.parent.rotations
    
    def update_angle(self):
        self.index_offset = self.calc_index_offset() * self.parent.length

    def get_frame(self):
        return self.parent.frames[self.index_offset + self.fnum].frame


class RotatedAnimationDataSet(animation.AnimationDataSet):
    def __init__(self, name, sprite, frames, parent, rotations):
        super().__init__(name, sprite, frames, parent)
        self.rotations = rotations
        self.rot_angle = 360//self.rotations
        # set up the rotated frames

    def create_rotated_frames(self):
        for rot in range(1, self.rotations):
            for f in range(self.length):
                result = animation.FrameData(f, True, False, self.frames[f].source_size, rect_to_dict(self.frames[f].sprite_source_location), self.frames[f].duration)
                result.oframe = pygame.transform.rotate(self.frames[f].oframe, rot * self.rot_angle)
                result.frame = result.oframe
                # rotate hitbox
                hbox = self.frames[f].hitbox
                for i in range(int(rot * self.rot_angle / 90)%4):
                    hbox = rot_rect_90deg(hbox, self.frames[f].ohitbox)
                result.hitbox = hbox
                self.frames.append(result)
    
    def get_registry(self):
        return RotatedRegistry(self)





