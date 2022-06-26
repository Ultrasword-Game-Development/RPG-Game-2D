"""
SpriteSheet

create spritesheet
- loads an image and make a spritesheet


"""


from engine import filehandler, window
from engine.world import Tile, register_tile_type
from engine.globals import *

from dataclasses import dataclass

# ------------ all loaded sprite sheets thing ----------- #

SPRITE_SHEETS_CONTAINER = {}
SPRITE_SHEETS_CACHE = {}

def register_sprite_sheet(sprite_sheet_name, sprite_sheet_object):
    """Register the sprite sheet object to global sprite sheet cache"""
    SPRITE_SHEETS_CONTAINER[sprite_sheet_name] = sprite_sheet_object


def get_sprite_sheet(path: str, s_width: int, s_height: int, spacing_x: int = 0, spacing_y: int = 0):
    """Get a sprite sheet"""
    if SPRITE_SHEETS_CACHE.get(path):
        return SPRITE_SHEETS_CACHE[path]
    obj = SpriteSheet(path, s_width, s_height, spacing_x, spacing_y)
    SPRITE_SHEETS_CACHE[path] = obj
    return obj

# ------------ SpriteData ----------------- #

@dataclass(init=False)
class SpriteData:
    """
    Contains variables:

    - the index of the sprite sheet
    - spritesheet area
        - where origin data is stored on the sprite sheet
    - the actual sprite image
    """

    index: int
    x: int
    y: int
    w: int
    h: int

    # not actually an int
    parent_object: int

    def __init__(self, index: int, x: int, y: int, w: int, h: int, img_path: str, tex):
        """Sprite data constructor"""
        self.index = index
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image_path = img_path
        self.tex = tex
    
    def get_area(self) -> list:
        """Return a list for the area that the sprite tile takes up in the spritesheet"""
        return [self.x, self.y, self.w, self.h]
    
    @staticmethod
    def create_data_from_single_image(image_path: str):
        """Create a SpriteData object from a single image"""
        img = filehandler.get_image(image_path)
        size = img.get_size()
        return SpriteData(-1, 0, 0, size[0], size[1], image_path, img)


# ------------- SpriteTile ----------------- #

@dataclass(init=False)
class SpriteTile(Tile):
    """
    Sprite Tile object

    contains data and a render function!
    - child of Tile

    - GOES INTO CHUNKS

    Tile:
        x: int
        y: int
        img: str
        collide: int
    """

    # a SpriteData pointer reference object thingy idk what python does with complex objects anymore
    sprite_data: SpriteData
    sprite_hashed_name: str

    def __init__(self, x: int, y: int, img: str, collide: int, sprite_data):
        """Sprite Tile constructor"""
        super().__init__(x, y, None, collide)

        self.sprite_data = sprite_data
        self.sprite_hashed_name = self.genereate_hash_str()
        self.img = self.sprite_data.parent_object.sheet_path
        self.tile_type = "sprite_tile"

        # set private variables
        self.data[SPRITETILE_SHEET_KEY] = sprite_data.parent_object.sheet_path
        self.data[SPRITETILE_SHEET_DATA_KEY] = sprite_data.parent_object.get_data()# an array of length 3
        self.data[SPRITETILE_SHEET_INDEX_KEY] = sprite_data.index


    def render(self, surface, images: dict, offset: tuple = (0, 0)) -> None:
        """Render function for this sprite tile"""
        if self.img:
            surface.blit(images[self.sprite_hashed_name], (self.x + offset[0], self.y + offset[1]))
    
    def cache_image(self, cache: dict) -> None:
        """Cache the image"""
        # we somehow need to hash the image
        cache[self.sprite_hashed_name] = filehandler.scale(self.sprite_data.tex, CHUNK_TILE_AREA)

    def genereate_hash_str(self) -> str:
        """Generate a hash string"""
        return f"{self.sprite_data.parent_object.sheet_path}-{self.sprite_data.index}"

    @staticmethod
    def deserialize(data: dict):
        """
        Deserialize method for Sprite Tiles
        """
        # check if loaded already
        extra = data[TILE_EXTRA_DATA_KEY]
        path = extra[SPRITETILE_SHEET_KEY]
        index = extra[SPRITETILE_SHEET_INDEX_KEY]
        stats = extra[SPRITETILE_SHEET_DATA_KEY] # contains the path , spacing , and sprite area
        if not SPRITE_SHEETS_CONTAINER.get(path):
            # if not, then load it
            SpriteSheet(path, stats[2][0], stats[2][1], stats[1][0], stats[1][1])
        
        # get the sprite sheet
        sheet = SPRITE_SHEETS_CONTAINER[path]
        
        result = SpriteTile(data[TILE_X_KEY], data[TILE_Y_KEY], data[TILE_COL_KEY], sheet.get_sprite(index))
        return result

# ------------- SpriteSheet ----------------- #

class SpriteSheet:
    """
    Sprite Sheet object

    - stores the path to the image
    - an array of sprite objects
    """

    def __init__(self, image: str, sprite_width: int, sprite_height: int, x_space: int = 0, y_space: int = 0):
        """Sprite Sheet Constructor"""
        self.sheet_path = image
        self.sheet = filehandler.get_image(image)
        self.sprites = []
        self.area = self.sheet.get_size()
        self.spacing = (x_space, y_space)
        self.sprite_area = (sprite_width, sprite_height)
        # get sprite count
        
        self.sprite_count = 0
        self.sprite_x_count = self.area[0] // self.sprite_area[0]
        self.sprite_y_count = self.area[1] // self.sprite_area[1]

        # load the images
        self.create()

        register_sprite_sheet(self.sheet_path, self)

    def create(self):
        """Create spritesheet"""
        left = self.spacing[0]
        top = self.spacing[1]

        sprite_count = 0
        while True:
            # get area
            new_img = filehandler.make_surface(self.sprite_area[0], self.sprite_area[1], filehandler.SRC_ALPHA)
            filehandler.crop_image(self.sheet, new_img, (left, top, left + self.sprite_area[0], top + self.sprite_area[1]))
            sprite_tile = SpriteData(sprite_count, left, top, self.sprite_area[0], self.sprite_area[1], self.sheet_path, new_img)
            sprite_tile.parent_object = self
            self.sprites.append(sprite_tile)
            sprite_count += 1

            # calculate next position
            left += self.sprite_area[0] + self.spacing[0]
            if left >= self.area[0]:
                left = self.spacing[0]
                top += self.sprite_area[1] + self.spacing[1]
                if top >= self.area[1]:
                    break
        self.sprite_count = sprite_count

    def iterate_images(self):
        """Iterate thorugh images"""
        for i in range(len(self.sprites)):
            yield self.sprites[i]

    def get_sprite(self, index: int) -> SpriteData:
        """Get a sprite data object"""
        return self.sprites[index]

    def get_data(self) -> list:
        """Get the data for this SpriteSheet"""
        return [self.sheet_path, self.spacing, self.sprite_area]

# --------- yes
register_tile_type(SpriteTile.tile_type, SpriteTile)
