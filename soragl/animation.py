import soragl as SORA

if SORA.DEBUG:
    print("Activated animation.py")

import pygame
import json
import os

from soragl import misc


# ------------------------------ #
# frame data

class FrameData:
    def __init__(self, frame: int, duration: float, order: int):
        self.frame = frame
        self.duration = duration
        self.order = order

    def get_frame(self):
        """Get the frame"""
        return self.frame

    def get_rotated_frame(self, angle: float):
        """Get a rotated version of the frame"""
        return pygame.transform.rotate(self.frame, angle)
    
    def get_scaled_frame(self, scale: float):
        """Get a scaled version of the frame"""
        return pygame.transform.scale(self.frame, scale)
    
    def get_rotated_scaled_frame(self, angle: float, scale: float):
        """Get a rotated and scaled version of the frame"""
        return pygame.transform.rotozoom(self.frame, angle, scale)


# ------------------------------ #
# spritesheet!

class SpriteSheet:
    """
    Sprite sheet
    - given a big boi image --> split into multiple smaller pygame surfaces!
    - given the width, height, spacex, spacey of each frame
        - we split into smaller surfaces
        - that can be accessed by ANIMATIONS + user if required
    """
    DEFAULT_FRAME_LENGTH = 1/10

    def __init__(self, image: pygame.Surface, width: int, height: int, spacex: int, spacey: int):
        self.image = image # filled with FrameData objects
        self.width = width
        self.height = height
        self.spacex = spacex
        self.spacey = spacey
        self.frames = []
        if self.image:
            self.generate_frames()
    
    def generate_frames(self):
        """Generate the frames"""
        # parse out frames!!
        self.frames.clear()
        mx, my = self.image.get_size()
        x, y, i = self.spacex, self.spacey, 0
        while y < my:
            while x < mx:
                self.frames.append(FrameData(self.image.subsurface(x, y, self.width, self.height), 
                        SpriteSheet.DEFAULT_FRAME_LENGTH, i))
                x += self.width + self.spacex
                i += 1
            x = self.spacex
            y += self.height + self.spacey
        # easy :D
    
    def __len__(self):
        """Get the number of frames"""
        return len(self.frames)

    def __getitem__(self, index: int):
        """Get a frame at a specified index"""
        # print(self.frames)
        return self.frames[index].get_frame()
    
    def get_frame_data(self, index: int):
        """Get the frame data at a specified index"""
        return self.frames[index]
    
    def __iter__(self):
        """Iterate over the frames"""
        return iter(self.frames)


# ------------------------------ #
# frame registry

class SequenceRegistry:
    def __init__(self, parent):
        """Allows access to animation sequence"""
        self.parent = parent
        self.findex = 0
        self.f = 0
        self.fdata = parent.get_frame_data(self.f)
        self.timer = SORA.get_timer(limit=self.fdata.duration, loop=True)

    def update(self):
        self.timer.update()
        if self.timer.loopcount:
            self.f += 1
            self.f %= len(self.parent)
            self.fdata = self.parent.get_frame_data(self.f)
            self.timer.reset_timer(self.fdata.duration)
    
    def get_frame(self):
        """Get the current animation frame"""
        return self.fdata.frame


# ------------------------------ #
# sequence

class Sequence:
    # ------------------------------ #
    # animation sequence
    def __init__(self, frames: list, metadata: dict):
        # cannot manipulate this
        self.sprite_sheet = SpriteSheet(None, 0, 0, 0, 0)
        self.sprite_sheet.frames = frames
        self.duration = sum([f.duration for f in frames])
        self._metadata = metadata

    def get_frame_data(self, index: int):
        """Get a frame at a specified index"""
        return self.sprite_sheet.get_frame_data(index)
    
    def get_frame(self, index: int):
        """Get a frame at a specified index"""
        return self.sprite_sheet[index]
    
    def get_duration(self):
        """Get the total duration of the animation sequence"""
        return self.duration

    def __len__(self):
        """Get the number of frames in the sequence"""
        return len(self.sprite_sheet)

    def __iter__(self):
        """Iterate over the frames in the sequence"""
        return iter(self.sprite_sheet)
    
    def get_registry(self):
        """Get a sequence registry"""
        return SequenceRegistry(self)


# ------------------------------ #
# animation categories

class Category:
    SEQUENCES = {}

    @classmethod
    def load_category(cls, filename: str):
        """Load animation category"""
        meta, pframe = cls.load_from_dict(json.loads(misc.fread(filename)), os.path.dirname(filename))
        sequences = {}
        for each in pframe:
            sequences[each] = Sequence(pframe[each], meta)
        cls.SEQUENCES[filename] = {"meta": meta, "framedata": sequences}
    
    @classmethod
    def get_category_framedata(cls, filename: str):
        """Return the animation parsed framedata"""
        return cls.SEQUENCES[filename]["framedata"]
    
    @classmethod
    def get_category_metadata(cls, filename: str):
        """Return the animation metadata"""
        return cls.SEQUENCES[filename]["meta"]

    @classmethod
    def load_from_dict(cls, data: dict, parent_folder: str):
        """
        Load a sequence given data
        Format (aseprite):
        - frames
        - meta
        """
        meta = data["meta"]
        frames = data["frames"]
        # parse frames
        pframes = {}
        spritesheet = SORA.load_image(os.path.join(parent_folder, meta["image"]))
        for f in frames:
            name = f["filename"]
            frame = f["frame"]
            sprite_source_size = f["spriteSourceSize"]
            source_size = f["sourceSize"]
            duration = f["duration"] / 1000
            # parse name string
            cat, ani, fnum = ".".join(name.split('.')[:-1]).split('-')
            fnum = int(fnum)
            if ani == '':
                ani = 'default'
            
            # extract frame data --> yeet into pygame surfacea
            surf = spritesheet.subsurface((frame['x'], frame['y']), (frame['w'], frame['h']))
            # make framedata -- other data kept out because unnecassary
            fdata = FrameData(surf, duration, fnum)

            # input into pframes
            if not ani in pframes:
                pframes[ani] = []
            pframes[ani].append(fdata)
        # return pframe
        return (meta, pframes)


