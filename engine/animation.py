import os
import json
from engine import filehandler, spritesheet
from engine.globals import *


ANIMATION_NAME = "name"
ANIMATION_IMAGES = "images"
ANIMATION_FRAME_TIMES = "times"
ANIMATION_FRAME_SIZE = "sizes"


animation_handler_cache = {}


def cache_animations(animation_data: dict):
    """Create Animation Handler object and cache everything"""
    global animation_handler_cache

    name = animation_data[ANIMATION_NAME]
    images = animation_data[ANIMATION_IMAGES]
    sizes = animation_data[ANIMATION_FRAME_SIZE]
    frame_time = animation_data[ANIMATION_FRAME_TIMES]

    animation_handler_cache[name] = AnimationHandler(name, images, sizes, frame_time)


# ------------- Animation Registry --------------- //
REGISTRY_COUNT_ID = 0

def GET_REGISTRY():
    """Get the Registry"""
    global REGISTRY_COUNT_ID
    REGISTRY_COUNT_ID += 1
    return REGISTRY_COUNT_ID


class AnimationRegistry:
    def __init__(self, handler):
        """
        Animation Registry constructor
        
        Stores the following
        - current frame num
        - delta time for current frame
        - changed flag
        - frame_dimensions: tuple(int, int)
        - the parent animation handler object

        """
        self.frame = 0
        self.time_passed = 0
        self.changed = True
        self.frame_dim = handler.image_sizes[self.frame]

        # animatino handler
        self.handler = handler
    
    def update(self, dt: float) -> None:
        """Update Animation Registry"""
        self.time_passed += dt
        if self.time_passed > self.handler.frame_time:
            self.time_passed -= self.handler.frame_time
            self.frame += 1
            self.changed = True
            if self.frame >= self.handler.frame_count:
                self.frame = 0
        
    def get_frame(self):
        """Get the current frame"""
        return self.handler.images[self.frame]

    def serialize(self) -> dict:
        """
        Serialize Animation Registry

        - store the animatin registry key
        """
        result = {}
        result[ANIMATION_PATH_KEY] = self.handler.json_path
        result[ANIMATION_NAME_KEY] = self.handler.name
        result[ANIMATION_ISSPRITESHEET_KEY] = self.handler.is_spritesheet
        return result

# -------------- image loading functions ------------- #

def iterate_load_image_list(base: str, images: list, ext: str = "", pre: str = "") -> iter:
    """Load images and yield them"""
    for img in images:
        # print(os.path.join(base, pre + img + ext))
        yield filehandler.get_image(os.path.join(base, (pre if pre else "") + img +( ext if ext else "")))


def load_image_list(base: str, images: list, ext: str = "", pre: str = "")-> list:
    """Load images from a list of strings"""
    return list(iterate_load_image_list(base, images, ext=ext))


class AnimationHandler:
    def __init__(self, json_path: str, name: str, images: list, image_sizes: list, fps: int, is_spritesheet: bool = False):
        """
        Animation Handler constructor
        
        Stores the animation data for a particular animation
        - the name of the animation
        - images in the animation
        - image sizes: in case frame must stretch | no need for slow image scaling from software
        - ideal frame_time for good animation fps
        - frame count: int - number of frames in animation
        """

        self.json_path = json_path
        self.name = name
        self.images = images
        self.image_sizes = image_sizes
        self.frame_time = 1/fps
        self.frame_count = len(images)

        self.is_spritesheet = is_spritesheet

    def get_registry(self) -> AnimationRegistry:
        """Register a registry to this animation handler"""
        return AnimationRegistry(self)

    @staticmethod
    def deserialize(data: dict):
        """
        Deserialize Animation Registry

        - get data, decode, ez
        """
        if data[ANIMATION_ISSPRITESHEET_KEY]:
            return create_animation_handler_from_sprite_sheet(data[ANIMATION_PATH_KEY])
        return create_animation_handler_from_json(data[ANIMATION_PATH_KEY])
        # print("Implement Deserializaetion for Animatino Registry please")


def create_animation_handler_from_json(json_path: str) -> AnimationHandler:
    """Create an animatino handler object from json file"""
    # check if already opened
    global animation_handler_cache
    if animation_handler_cache.get(json_path):
        return animation_handler_cache[json_path]

    # cont
    with open(json_path, 'r') as file:
        data = json.load(file)
        file.close()
    name = data["name"]
    base_path = data["base_path"]
    image_paths = data["images"]
    fps = data["fps"]
    pre = data.get("pre", "")
    ext = data.get("ext", "")
    sizes = data.get("sizes")
    size = data.get("size")
    
    dif_sizes = sizes != None
    # load images
    result_images = []
    for i, result in enumerate(iterate_load_image_list(base_path, image_paths, ext=ext, pre=pre)):
        if dif_sizes:
            # you should index to the right size
            result_images.append(filehandler.scale(result, sizes[i]))
        else:
            # just stick
            result_images.append(filehandler.scale(result, size))
    
    # create animation handler
    r = AnimationHandler(json_path, name, result_images, sizes if dif_sizes else [size for i in range(len(image_paths))], fps)
    animation_handler_cache[json_path] = r
    return r


def create_animation_handler_from_sprite_sheet(json_path: str) -> AnimationHandler:
    """Create an animation handler from sprite sheet json"""
    # check if already opened
    global animation_handler_cache
    if animation_handler_cache.get(json_path):
        return animation_handler_cache[json_path]
    
    # open
    with open(json_path, 'r') as file:
        data = json.load(file)
        file.close()
    
    name = data["name"]
    base_path = data["base_path"]
    image_path = data["image"]
    sprite_area = data["sprite_area"]
    fps = data["fps"]
    size = data["size"]
    spacing = data["spacing"]
    pre = data.get("pre", "")
    ext = data.get("ext", "")

    # create sprite sheet
    sprite_sheet = spritesheet.get_sprite_sheet(os.path.join(base_path, (pre if pre else "") + image_path +( ext if ext else "")), 
                sprite_area[0], sprite_area[1], spacing_x=spacing[0], spacing_y=spacing[1])

    # resize all images
    resized = []
    for img in sprite_sheet.iterate_images():
        resized.append(filehandler.scale(img.tex, size))

    # create animation handler
    result = AnimationHandler(json_path, name, resized, [size] * len(resized), fps, is_spritesheet=True)
    animation_handler_cache[json_path] = result
    return result

