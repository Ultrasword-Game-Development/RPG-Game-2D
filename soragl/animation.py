# ------------------------------ #

import soragl as SORA

if SORA.DEBUG:
    print("Activated animation.py")

import pygame
from pygame import transform as pgtrans

import json
import os

from soragl import misc, smath

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

    DEFAULT_FRAME_LENGTH = 1 / 10

    def __init__(
        self, image: pygame.Surface, width: int, height: int, spacex: int, spacey: int
    ):
        self.image = image  # filled with FrameData objects
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
                self.frames.append(
                    FrameData(
                        self.image.subsurface(x, y, self.width, self.height),
                        SpriteSheet.DEFAULT_FRAME_LENGTH,
                        i,
                    )
                )
                x += self.width + self.spacex
                i += 1
            x = self.spacex
            y += self.height + self.spacey

    def get_frame_data(self, index: int):
        """Get the frame data at a specified index"""
        return self.frames[index]

    def __len__(self):
        """Get the number of frames"""
        return len(self.frames)

    def __getitem__(self, index: int):
        """Get a frame at a specified index"""
        # print(self.frames)
        return self.frames[index].get_frame()

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
        self.fini = 0
        self.fdata = parent.get_frame_data(self.f)
        self.timer = SORA.get_timer(limit=self.fdata.duration, loop=True)

    def update(self):
        self.timer.update()
        if self.timer.loopcount:
            self.f += 1
            if self.f >= len(self.parent):
                self.f = 0
                self.fini += 1
            self.fdata = self.parent.get_frame_data(self.f)
            self.timer.reset_timer(self.fdata.duration)

    def get_frame(self):
        """Get the current animation frame"""
        return self.fdata.frame

    def finished_loops(self) -> int:
        """Get the # of finished animatino cycles"""
        return self.fini

    def reset(self):
        """Reset the registry frames"""
        self.f = 0
        self.fini = 0

# ------------------------------ #
# sequence

class Sequence:
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

    def get_registry(self):
        """Get a sequence registry"""
        return SequenceRegistry(self)

    def __len__(self):
        """Get the number of frames in the sequence"""
        return len(self.sprite_sheet)

    def __iter__(self):
        """Iterate over the frames in the sequence"""
        return iter(self.sprite_sheet)

# ------------------------------ #
# animation categories

class Category:
    """
    Categories store data on:
    - framedata; dict of sequences
    - meta; dict of metadata

    framedata:
    - key: name of sequence
    - value: a Sequence object (contains all the frames)
        - to use --> get a registry object from the sequence
    """

    SEQUENCES = {}

    @classmethod
    def load_category(cls, filename: str):
        """Load animation category"""
        meta, pframe = cls.load_from_dict(
            json.loads(misc.fread(filename)), os.path.dirname(filename)
        )
        sequences = {}
        for each in pframe:
            sequences[each] = Sequence(pframe[each], meta)
        cls.SEQUENCES[filename] = {"meta": meta, "framedata": sequences}

    @classmethod
    def load_spritesheet_from_directory(cls, folder: str, options: dict = {}):
        """
        Load animation from directory of images
        - directory should contain images of same name + numbered for sorting
        """
        _files = sorted(os.listdir(folder))
        # load all image files
        dx = options.get("dx", 0)
        dy = options.get("dy", 0)
        print(dx, dy)
        result = SpriteSheet(None, 0, 0, 0, 0)
        result.image = folder
        for i, f in enumerate(_files):
            if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg"):
                _image = SORA.load_image(os.path.join(folder, f))
                sx, sy = _image.get_size()
                if not dx: dx = sx
                if not dy: dy = sy
                _image = SORA.scale_image(_image, (dx, dy))
                result.frames.append(FrameData(_image, 100, i))
                result.height = max(result.height, _image.get_height())
                result.width += _image.get_width()
        return result
    
    @classmethod
    def sequence_from_spritesheet(cls, spritesheet: SpriteSheet):
        """Create an sequence (animation) from a spritesheet"""
        return Sequence(spritesheet.frames, {
            "app": "sora",
            "version": SORA._VERSION,
            "image": spritesheet.image,
            "format": "RGBA8888",
            "size": {
                "w": spritesheet.width,
                "h": spritesheet.height
            }
        })
    
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
            cat, ani, fnum = ".".join(name.split(".")[:-1]).split("-")
            fnum = int(fnum)
            if ani == "":
                ani = "default"

            # extract frame data --> yeet into pygame surface
            surf = spritesheet.subsurface(
                (frame["x"], frame["y"]), (frame["w"], frame["h"])
            )
            # make framedata -- other data kept out because unnecassary
            fdata = FrameData(surf, duration, fnum)

            # input into pframes
            if not ani in pframes:
                pframes[ani] = []
            pframes[ani].append(fdata)
        # return pframe
        return (meta, pframes)

    @classmethod
    def load_from_directory(cls, folder: str, options: dict = {}):
        """Load a sequence from a directory"""
        # load all image files
        ss = cls.load_spritesheet_from_directory(folder, options=options)
        seq = cls.sequence_from_spritesheet(ss)
        cls.add_sequence(folder, seq._metadata, seq)

    #===
    @classmethod
    def add_sequence(cls, name: str, meta: dict, sequence: Sequence):
        """Add a sequence to the category"""
        cls.SEQUENCES[name] = {"meta": meta, "framedata": {name: sequence}}

    @classmethod
    def get_registries_for_all(cls, filename: str):
        """Get a dictionary of registries for all sequences in a category"""
        return {
            k: v.get_registry() for k, v in cls.get_category_framedata(filename).items()
        }
        
    @classmethod
    def get_category_framedata(cls, filename: str):
        """Return the animation parsed framedata"""
        return cls.SEQUENCES[filename]["framedata"]

    @classmethod
    def get_category_metadata(cls, filename: str):
        """Return the animation metadata"""
        return cls.SEQUENCES[filename]["meta"]


def generate_options(width: int = 0, height: int = 0):
    """Generate options for loading a spritesheet"""
    return {"dx": width, "dy": height}

# -------------------------------------------------- #
# extensions
# ------------------------------ #
# rotated-sequences

class RotatedRegistry(SequenceRegistry):
    def __init__(self, parent, angle):
        super().__init__(parent)
        self.angle = angle

    def update(self):
        self.timer.update()
        if self.timer.loopcount:
            self.f += 1
            self.f %= len(self.parent)
            self.fdata = self.parent.get_frame_data(self.f, self.angle)
            self.timer.reset_timer(self.fdata.duration)

    def get_frame(self):
        """Get the current animation frame"""
        return self.fdata.get_frame()

class RotatedSequence(Sequence):
    @classmethod
    def generate_angles(cls, start: int, end: int, skip: int):
        """Generate angles"""
        return list(range(start, end, skip))
    # ------------------------------ #
    def __init__(self, sequence: "Sequence", angle_range: tuple = (0, 360, 30)):
        super().__init__([], sequence._metadata)
        # angle range
        self.angle_range = angle_range
        # rotate frames - angles
        frames = sequence.sprite_sheet.frames
        for a in range(self.angle_range[0], self.angle_range[1], self.angle_range[2]):
            for i in range(len(frames)):
                r_frame = pgtrans.rotate(frames[i].frame, a)
                r_data = FrameData(r_frame, frames[i].duration, frames[i].order)
                self.sprite_sheet.frames.append(r_data)
        # duration
        self.duration = sequence.duration
        self._size = len(sequence)
    
    # ------------------------------ #
    def get_frame_data(self, index, angle: float=0):
        """Get a frame at a specified index and angle"""
        # prob fix this 1:15am code
        offset = round(smath.__clamp__(angle % 360, 0, 360) / self.angle_range[2])
        # return super().get_frame_data(index * len(self) + offset)
        return super().get_frame_data(index + offset * len(self))

    def get_frame(self, index: int, angle:float=0):
        """Get a frame at a specified index and angle"""
        # prob fix this 1:15am code
        offset = round(smath.__clamp__(angle % 360, 0, 360) / self.angle_range[2])
        # return super().get_frame(index + offset * len(self))
        return super().get_frame(index * len(self) + offset)

    def get_registry(self, angle: float=0):
        """Get a sequence registry"""
        return RotatedRegistry(self, angle)

    # ------------------------------ #
    def __len__(self):
        """Get the number of frames in the sequence"""
        return self._size

