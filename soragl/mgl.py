import soragl as SORA

if SORA.DEBUG:
    print("Activated mgl.py")

from . import misc
import moderngl

import glm
import struct
import math
from array import array
import numpy as np

import pygame.math as pgmath


# ------------------------------------------------------------ #
# moderngl object -- :l
# ------------------------------------------------------------ #


# moderngl singleton
class ModernGL:
    # ------------------------------ #
    # modern gl globals
    CTX = None
    CLEARCOLOR = [0.0, 0.0, 0.0, 1.0]

    # ------------------------------ #
    # static
    FB_BUFFER = None

    # ------------------------------ #
    @classmethod
    def create_context(cls, options: dict):
        """Creates moderngl context."""
        cls.CTX = moderngl.create_context(options["standalone"])
        cls.CTX.gc_mode = options["gc_mode"] if "gc_mode" in options else None
        cls.CLEARCOLOR = (
            options["clear_color"] if "clear_color" in options else ModernGL.CLEARCOLOR
        )
        # create the quad buffer for FB
        print("quad buffer needs to be replaced with custom vao object")
        cls.FB_BUFFER = cls.CTX.buffer(
            data=array(
                "f",
                [
                    -1.0,
                    -1.0,
                    0.0,
                    0.0,
                    1.0,
                    -1.0,
                    1.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    -1.0,
                    1.0,
                    0.0,
                    1.0,
                ],
            )
        )
        # stuff
        if "depth_test" in options and options["depth_test"]:
            cls.CTX.enable(moderngl.DEPTH_TEST)

    @classmethod
    def update_context(cls):
        """Updates moderngl context."""

        # garbage collection
        cls.CTX.gc()

    @classmethod
    def render(cls, texture):
        """Renders the framebuffer to the window."""
        # render frame buffer texture to window!
        cls.CTX.screen.use()
        cls.CTX.enable(moderngl.BLEND)
        cls.CTX.clear(
            ModernGL.CLEARCOLOR[0],
            ModernGL.CLEARCOLOR[1],
            ModernGL.CLEARCOLOR[2],
            ModernGL.CLEARCOLOR[3],
        )

        cls.CTX.disable(moderngl.BLEND)

    @classmethod
    def set_clear_color(cls, color):
        """Sets the clear color."""
        cls.CLEARCOLOR = color


# ------------------------------ #
# textures
class Texture:
    """
    Texture class
    - handles textures, pygame to gltex conversion, loading textures, etc
    """

    # ------------------------------ #
    TEXTURES = {}

    @classmethod
    def load_texture(cls, path):
        """Loads a moderngl texture from a file."""
        surf = soragl.SoraContext.load_image(path)
        return cls.pg2gltex(surf, path)

    @classmethod
    def pg2gltex(cls, surface, texname):
        """Converts pygame surface to moderngl texture."""
        c = 4
        if texname not in cls.TEXTURES:
            ntex = ModernGL.CTX.texture(surface.get_size(), c)
            ntex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            ntex.swizzle = "BGRA"  # TODO - swapped this
            cls.TEXTURES[texname] = ntex
        # upload texture data to GPU
        tdata = surface.get_view("1")
        cls.TEXTURES[texname].write(tdata)
        return cls.TEXTURES[texname]
        return self.texture.height

    # ------------------------------ #
    def __init__(self, texture):
        """Load texture with other data"""
        self.texture = texture
        self.data = {}

    def set_data(self, data):
        """Set texture data"""
        self.data = data

    def use(self, location=0):
        self.texture.use(location)


# texture handler
class TextureHandler:
    def __init__(self):
        """Create TextureHandler object"""
        self.textures = []
        self._tex_id_buf = struct.pack(
            "9i", *[i for i in range(9)]
        )  # TODO: add this -->  , mgl.GL_STATIC_DRAW / DYNAMIC DRAW

    def add_texture(self, texture):
        """Adds a texture to the handler"""
        self.textures.append(texture)

    def create_and_add_texture(self, path: str):
        """Create and add new texture"""
        self.add_texture(Texture.load_texture(path))

    def get_texture(self, index):
        """Gets a texture from the handler"""
        return self.textures[index]

    def remove_texture(self, index):
        """Removes a texture from the handler"""
        self.textures.pop(index)

    def get_textures(self):
        """Gets all textures from the handler"""
        return self.textures

    def get_texture_count(self):
        """Gets the number of textures in the handler"""
        return len(self.textures)

    def bind_textures(self, vao, var_name: str):
        """Binds all textures in the handler"""
        for i in range(1, len(self.textures) + 1):
            self.textures[i - 1].use(location=i)
        vao.change_uniform_vector(var_name, self._tex_id_buf)

    def unbind_textures(self):
        """Unbinds all textures in the handler"""
        for i in range(len(self.textures)):
            self.textures[i].use(location=0)

    def clear_textures(self):
        """Clears all textures in the handler"""
        self.textures = []

    def load_texture(self, image: str):
        """Loads a texture from a file."""
        self.textures.append(Texture.load_texture(image))


# ------------------------------ #
# shaders


# step
class ShaderStep:
    """
    Shader Steps!!!
    - vertex or fragment for now
    """

    VERTEX = 0
    FRAGMENT = 1

    SNIPPETS = ["#vertex", "#fragment"]

    def __init__(self, shadersnippet: str):
        """Stores data for shaderstep"""
        # determine what type of shader it is
        pre = shadersnippet.split("\n")[1:][:-1]
        if pre[0] not in self.SNIPPETS:
            raise Exception("Invalid shader snippet")
        self.shadertype = self.SNIPPETS.index(pre[0])
        self.shader = shadersnippet[len(self.SNIPPETS[self.shadertype]) + 2 :]


# program
class ShaderProgram:
    """
    Takes input file.glsl and compiles it into a shader program.
    - Single file format!
    """

    PIPELINE_SPLIT = "###"

    def __init__(self, path):
        self.path = path
        # extract vert + frag shaders
        data = misc.fread(path)
        # separate into Vertex and Fragment shaders
        self.sections = [
            ShaderStep(shadersnippet)
            for shadersnippet in data.split(ShaderProgram.PIPELINE_SPLIT)[1:]
        ]
        self.sections.sort(key=lambda x: x.shadertype)
        # create program
        print(self.path)
        self.program = ModernGL.CTX.program(
            vertex_shader=self.sections[0].shader,
            fragment_shader=self.sections[1].shader,
        )

    @classmethod
    def update_uniforms(cls, s: str, uniforms: dict):
        """Update uniforms"""
        tcount = 0
        shader = cls.SHADERS[s]
        for uni in uniforms:
            # check if texture type
            try:
                # print(uniforms[uni], type(uniforms[uni]))
                if type(uniforms[uni][0]) == moderngl.texture.Texture:
                    uniforms[uni][0].use(location=tcount)
                    shader.program[uni].value = tcount
                    tcount += 1
                elif uniforms[uni][1] == VAO.SCALAR:
                    shader.program[uni].value = uniforms[uni][0]
                elif uniforms[uni][1] == VAO.VECTOR:
                    shader.program[uni].write(uniforms[uni][0])
                else:
                    print("bad uniform type")
            except Exception as e:
                print(
                    f"Error occured when uploading uniform: `{uni}` | of value: {uniforms[uni]}"
                )
                print(e)
                soragl.SoraContext.pause_time(0.4)

    # ------------------------------ #
    # loading shaders
    SHADERS = {}
    DEFAULT = "assets/shaders/default.glsl"

    @classmethod
    def load_shader(cls, path=None):
        """Load a shader into gl"""
        if not path:
            return cls.load_shader(cls.DEFAULT)
        if path in cls.SHADERS:
            return cls.SHADERS[path]
        cls.SHADERS[path] = ShaderProgram(path)
        return cls.SHADERS[path]


# ------------------------------ #
# buffers!
class Buffer:
    """
    Buffer class
    - handles buffers = vao, vbo, ibo, buffers!
    """

    def __init__(self, parse: str, data: list, dynamic=False):
        """Create a Buffer object"""
        self.rawbuf = data.copy()
        self.parse = parse
        packed = struct.pack(parse, *self.rawbuf)
        # create ctx buffer
        self.buffer = ModernGL.CTX.buffer(packed, dynamic=dynamic)

    def get_buffer(self):
        """Get the buffer"""
        return self.buffer

    def get_raw(self):
        """Get the raw buffer"""
        return self.rawbuf

    def update_raw(self, parse: str, data: list):
        """Update the raw buffer"""
        self.parse = parse
        self.rawbuf = data.copy()
        self.update_buffer()

    def update_buffer(self):
        """Update the buffer"""
        packed = struct.pack(self.parse, *self.rawbuf)
        self.buffer.write(packed)

    def render(self):
        """Render the buffer"""
        pass


# ------------------------------ #
# uniform handler
class UniformHandler:
    """
    Uniform Handler
    - handles uniform values
    """

    SCALAR = 0
    VECTOR = 1

    def __init__(self, shader_path: str = ShaderProgram.DEFAULT):
        """Creates an empty uniform handler"""
        self.uniforms = {}
        self.shader = shader_path
        # load the shader in mgl context
        ShaderProgram.load_shader(shader_path)

    def change_uniform_scalar(self, name: str, value):
        """Change a uniform value"""
        self.uniforms[name] = (value, self.SCALAR)

    def change_uniform_vector(self, name: str, value):
        """Change a uniform value"""
        self.uniforms[name] = (value, self.VECTOR)

    def __getitem__(self, key):
        """Get an item"""
        return self.uniforms[key]

    def __setitem__(self, key, value):
        """Set an item"""
        self.uniforms[key] = value

    def update(self):
        """Update the uniforms"""
        ShaderProgram.update_uniforms(self.shader, self.uniforms)


# ------------------------------ #
# vertex attribute object
class VAO:
    """
    Vertex Attribute Objects
    - very useful -- layout for vertices in the opengl context
    """

    SCALAR = 0
    VECTOR = 1

    def __init__(self, shader_path: str = ShaderProgram.DEFAULT):
        """Creates an empty VAO"""
        self.attributes = []
        self.vbo = None
        self.ibo = None
        self.vao = None
        self.uniforms = UniformHandler(shader_path)
        self.shader = shader_path
        self.initialized = False

    def add_attribute(self, parse: str, var_name: str):
        """Add an attribute to the vao"""
        self.attributes.append([parse, var_name])

    def change_uniform_scalar(self, name: str, value):
        """Change a uniform value"""
        self.uniforms.change_uniform_scalar(name, value)

    def change_uniform_vector(self, name: str, value):
        """Change a uniform value"""
        self.uniforms.change_uniform_vector(name, value)

    def get_uniform(self, name: str):
        """Get a uniform value"""
        return self.uniforms[name]

    def create_structure(self, vbo, ibo=None):
        """Creates the gl context for the vao"""
        self.vbo = vbo
        self.ibo = ibo
        # check if there are ibo
        if ibo:
            self.glvbo = self.vbo.buffer
            self.glibo = self.ibo.buffer
            # create the v attrib string
            blob = []
            vattrib = " ".join([i[0] for i in self.attributes])
            blob.append(
                tuple([self.glvbo, vattrib] + list(i[1] for i in self.attributes))
            )
            # vao object
            self.vao = ModernGL.CTX.vertex_array(
                ShaderProgram.SHADERS[self.shader].program, blob, self.glibo
            )
        else:
            self.glvbo = self.vbo.buffer
            vertices = np.asarray(self.vbo.rawbuf, dtype=np.float32)
            faces = np.arange(len(vertices), dtype=np.int32)
            # create index buffer for vertices
            points = ModernGL.CTX.buffer(faces)

            # create the v attrib string
            blob = []
            vattrib = " ".join([i[0] for i in self.attributes])
            blob.append(
                tuple([self.glvbo, vattrib] + list(i[1] for i in self.attributes))
            )
            # vao object
            self.vao = ModernGL.CTX.vertex_array(
                ShaderProgram.SHADERS[self.shader].program, blob, points
            )
        self.initialized = True
        # done?

    def render(self, mode=moderngl.TRIANGLES):
        """Render the vao given its data"""
        if not self.initialized:
            raise Exception("VAO has not yet been initialized!")
        # update uniform variables!
        self.uniforms.update()
        self.vao.render(mode=mode)

    def get_shader(self) -> str:
        """Get the shader"""
        return self.shader


# ------------------------------ #
# camera
class Camera:
    def __init__(self, pos, front, up, rot):
        # private

        # transformation
        self._position = glm.vec3(pos[0], pos[1], pos[2])
        self._front = glm.vec3(front[0], front[1], front[2])
        self._target = glm.vec3(front[0], front[1], front[2])
        self._rotation = glm.vec3(rot[0], rot[1], rot[2])

        # work on quaternions
        self._identity = glm.mat4(1.0)
        # self._rot = glm.quad(0, 0, 0, 0)

        # direction vectors
        self._up = glm.vec3(up[0], up[1], up[2])
        self._right = glm.vec3(0, 0, 0)

        self._view = None
        self._proj = None

    def calculate_properties(self):
        """Calculate the direction vectors"""
        # rotation
        # self._rotation.x = glm.clamp(self._rotation.x, -89.0, 89.0)
        # self._rotation.y = glm.clamp(self._rotation.y, -89.0, 89.0)
        # self._rotation.z = glm.clamp(self._rotation.z, -89.0, 89.0)

        # calculate directino
        self._target.x = glm.cos(glm.radians(self.yaw)) * glm.cos(
            glm.radians(self.pitch)
        )
        self._target.y = glm.sin(glm.radians(self.pitch))
        self._target.z = glm.sin(glm.radians(self.yaw)) * glm.cos(
            glm.radians(self.pitch)
        )

        self._target = glm.normalize(self._target)
        # right vec
        self._right = glm.normalize(glm.cross(self._target, self._up))

    def calculate_view_matrix(self):
        """Calculate the view matrix"""
        # self.calculate_properties()
        # rotation?
        return glm.lookAt(self._position, self._position + self._target, self._up)

    def get_view_matrix(self):
        """Get the view matrix"""
        return self._view

    def get_projection_matrix(self):
        """Get the projection matrix"""
        return self._proj

    @property
    def pitch(self):
        return self._rotation.y

    @pitch.setter
    def pitch(self, value):
        self._rotation.y = value

    @property
    def yaw(self):
        return self._rotation.x

    @yaw.setter
    def yaw(self, value):
        self._rotation.x = value

    @property
    def roll(self):
        return self._rotation.z

    @roll.setter
    def roll(self, value):
        self._rotation.z = value

    @property
    def front(self):
        """Get the front vector"""
        return self._front

    @property
    def right(self):
        """Get the right vector"""
        return self._right

    @property
    def position(self):
        return self._position

    @property
    def target(self):
        return self._target

    @property
    def up(self):
        return self._up

    @property
    def rotation(self):
        """Get the rotation of the camera"""
        return self._rotation

    def set_rotation(self, x, y, z):
        """Set the rotation of the camera"""
        self.calculate_properties()
        self._rotation = glm.vec3(x, y, z)
        self._view = self.calculate_view_matrix()

    def rotate(self, x, y, z):
        """Rotate the camera in radians"""
        self.calculate_properties()
        # set values
        self._rotation += glm.vec3(x, y, z)
        self._view = self.calculate_view_matrix()

    def translate(self, x, y, z):
        self.calculate_properties()
        self._position += glm.vec3(x, y, z)
        self._view = self.calculate_view_matrix()

    def r_translate(self, x, y, z):
        """Translate relative to the camera"""
        self.calculate_properties()
        self._position += self._right * x
        self._position += self._up * y
        self._position += self._target * z
        self._view = self.calculate_view_matrix()
