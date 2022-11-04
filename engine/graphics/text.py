# -------------------------------------------------- #
# text.py for text objects i guess
# -------------------------------------------------- #

import pygame

from ..misc import maths
from .. import singleton

# -------------------------------------------------- #
# text manager


class TextManager:
    """
    Text Manager

    text manager is a class used to render and handle text objects
    it stores a string with \n characters what will be newlined (move to newline when see \n)

    we also have colored text :)
    """

    # -------------------------------------------------- #
    # statics
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    COLOR_CHANGE_SYMBOL = '&;'
    COLOR_CHANGE_LEN = len(COLOR_CHANGE_SYMBOL)
    HEX_SIZE = 6

    # -------------------------------------------------- #

    def __init__(self, font, text: str, align: int, spacingx: int = 0, spacingy: int = 0, underline: bool = False,
                 bold: bool = False, italic: bool = False, newsection: str = '\p', newline: str = '\n', maxwidth: int = 0, aa: bool = False,
                 def_col: tuple = (255, 255, 255), background: tuple = (0, 0, 0, 0), buffer_is_text: bool=True):
        # text manager data
        self.font = font
        self.text = text
        self.text_buffer = self.text if buffer_is_text else ""
        self.align = align
        self.spacing = [spacingx, spacingy]
        self.newsection = newsection
        self.newline = newline
        self.maxwidth = maxwidth
        self.color = def_col
        # vfx
        self.underline = underline
        self.bold = bold
        self.italic = italic
        self.aa = aa
        self.config = {"font": font, "align": align, "spacing": self.spacing, "newsection": newsection, "newline": newline,
                       "underline": underline, "bold": bold, "italic": italic, "maxwidth": maxwidth, "aa": aa,
                       "color": def_col, "background": background}
        # give font settings
        self.font.set_underline(self.underline)
        self.font.set_bold(self.bold)
        self.font.set_italic(self.italic)
        # quick cache
        self.parts = []
        self.updated = False
        self.update_text()

        # text effects
        self.effects = []

    def render_text(self, surface, center, rel=False):
        """Renders directly to a surface given a center position"""
        self.update_text()
        # -------------------------------------------------- #
        # update the text effects
        for e in self.effects:
            e.update()
        # -------------------------------------------------- #
        # paragraphs --> words (allows for paragraph separation and individual text formatting
        area = [0, 0]
        for part in self.parts:
            iarea = part.get_area()
            # print(iarea)
            area[0] += iarea[0]
            area[1] += iarea[1]

        # render
        top = 0
        for part in self.parts:
            if rel:
                surface.blit(part.render_static(), (center[0] + singleton.WORLD_OFFSET_X, top + center[1] + singleton.WORLD_OFFSET_Y))
            else:
                surface.blit(part.render_static(), (center[0], top + center[1]))
            top += part.get_area()[1]
        for e in self.effects:
            e.post_update()

    def update_text(self):
        """Update the self.parts cache for text"""
        if not self.updated:
            self.updated = True
            self.parts = [Paragraph(paragraph, self.config) for paragraph in self.text_buffer.split(self.newsection)]

    def set_text(self, text: str) -> None:
        """Change the current text"""
        self.text = text
        self.updated = False

    def get_text(self) -> str:
        """Return the current text string"""
        return self.text

    def append_text(self, app: str) -> None:
        """Add text to current text string"""
        self.text += app
        # print(self.text)

    def append_to_buffer(self, app: str) -> None:
        """Add text to the rendering buffer"""
        self.text_buffer += app
        self.updated = False

    def add_effect(self, effect):
        """Add an effect to the text manager"""
        self.effects.append(effect)

    def remove_effect(self, effect):
        """Removes an effect given an effect"""
        self.effects.remove(effect)


# -------------------------------------------------- #
# paragraph objects

class Paragraph:
    NEW_LINE = "$nl"

    def __init__(self, text: str, config: dict):
        self.text = text
        self.config = config
        self.area = [0, 0]

    def render_static(self):
        """Return a surface with rendered text"""
        # we have an array of words - the goal is to render it with paragraph newline stuff
        color = self.config["color"]
        width = 0
        # just render all in a line -- but also remember to consider text coloring
        rendered = []
        # print(self.text.split(self.config["newsection"]))
        for line in self.text.split(self.config["newline"]):
            rendered.append([])
            width = 0
            for word in line.split():
                # each word if they start with the special sequence
                if word.startswith(TextManager.COLOR_CHANGE_SYMBOL):
                    # using hex btw
                    # next 6 character = color
                    color = maths.hex_to_tuple(word[TextManager.COLOR_CHANGE_LEN:TextManager.HEX_SIZE + TextManager.COLOR_CHANGE_LEN])
                    render = self.config["font"].render(word[TextManager.COLOR_CHANGE_LEN+TextManager.HEX_SIZE:], self.config["aa"], color, self.config["background"])
                # if they are just normal word
                else:
                    # just normal words :)
                    render = self.config["font"].render(word, self.config['aa'], color, self.config["background"])
                # add to render
                width += render.get_size()[0]
                # if we go out of width bounds - add a new line
                if width < self.config["maxwidth"] < width:
                    rendered.append([])
                rendered[-1].append(render.convert_alpha())

        # render spaces
        space_area = self.config["font"].render(" ", self.config["aa"], color, self.config["background"]).get_size()

        # find the area
        area = [0, 0]
        line_area = []
        for row in rendered:
            # row = [images]
            line_area.append([0, 0])
            # col = image
            for j, col in enumerate(row):
                size = col.get_size()
                line_area[-1][0] += size[0]
                line_area[-1][1] = max(line_area[-1][1], size[1])
                # print("word area", line_area[-1])
            line_area[-1][0] += (len(row) - 1) * space_area[0]
            # add max height size to the array
            area[0] = max(area[0], line_area[-1][0])
            area[1] += line_area[-1][1]

        # create surface
        # print("texture area: ", area)
        result = pygame.Surface(area, 0, 32).convert_alpha()

        # render!!!
        left = 0
        top = 0
        for i, row in enumerate(rendered):
            # calculate the left position
            if self.config["align"] == TextManager.ALIGN_CENTER:
                left = (area[0] - line_area[i][0]) // 2
            elif self.config["align"] == TextManager.ALIGN_LEFT:
                left = 0
            else:
                # assume is right
                left = area[0] - line_area[i][0]
            for col in row:
                # print("word coords", left, top)
                result.blit(col, (left, top))
                left += col.get_size()[0] + space_area[0]
            # move down
            top += line_area[i][1]
        self.area = area

        # finished finally
        result.set_colorkey((0, 0, 0))
        return result

    def get_area(self) -> list:
        """Get the area of the rendered text"""
        result = [0, 0]
        for line in self.text.split(self.config["newline"]):
            size = [0, 0]
            for word in line.split():
                # each word if they start with the special sequence
                if word.startswith(TextManager.COLOR_CHANGE_SYMBOL):
                    size = self.config["font"].size(word[TextManager.COLOR_CHANGE_LEN + TextManager.HEX_SIZE:])
                else:
                    # just normal words :)
                    size = self.config["font"].size(word)

                # increment size
                result[0] = max(result[0], size[0])
            result[1] += size[1]

        return result


# -------------------------------------------------- #
# typewriter effect text

class TextEffect:
    """
    update:
    - called before rendering
    - usually performs changes to the text -- like spell check if you want or whatever :)

    post_update:
    - called after rendering
    - you can add shadows and stuff
    - post-processing requires direct access to the text surface which should be:
    - TBD
    """
    print("text.py fix post update and text surface access please :)")
    # -------------------------------------------------- #
    # static
    CID = 0

    # -------------------------------------------------- #
    def __init__(self, text_manager):
        self.tm = text_manager
        TextEffect.CID += 1
        self.tid = f"effect{TextEffect.CID}"

    def update(self):
        pass

    def post_update(self):
        """Update after the render has been finished!"""
        pass

    def __eq__(self, other):
        """Comparison function :)"""
        if type(other) != TextEffect:
            return False
        return self.tid == other.tid

    def __hash__(self):
        """Hash the effect"""
        return hash(self.tid)






