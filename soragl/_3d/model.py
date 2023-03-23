import os

import soragl
from soragl import mgl

import glm


# ------------------------------ #
# model class


class Face:
    def __init__(self, v1: list, v2: list, v3: list):
        """Face object for .obj files"""
        self._v1 = v1
        self._v2 = v2
        self._v3 = v3

    def __iter__(self):
        """Iterate over vertices"""
        yield self._v1
        yield self._v2
        yield self._v3

    def __getitem__(self, index: int):
        """Get vertex at index"""
        if index == 0:
            return self._v1
        elif index == 1:
            return self._v2
        elif index == 2:
            return self._v3
        else:
            raise IndexError("Index out of range")


class Model:
    def __init__(self, vbuffer, texture):
        """Model object"""
        self._vbuffer = vbuffer
        self._texture = texture


# ------------------------------------------------------------ #
# model loader --
"""
For loading models
- .obj
- to add more
"""
# ------------------------------------------------------------ #


# loading models
class Loader:
    @classmethod
    def find_file_ext(cls, path: str, ext: str):
        """Find file with given ext"""
        for f in os.listdir(path):
            if f.endswith(ext):
                return os.path.join(path, f)

    @classmethod
    def find_files_with_ext(cls, path: str, ext: list):
        """Find all files with ext - in dir"""
        for f in os.listdir(path):
            for j in ext:
                if f.endswith(j):
                    yield os.path.join(path, f)
                    break

    # ------------------------------ #

    def __init__(self, path: str):
        self._path = path

        # load data into buffers
        # self._textures = mgl.TextureHandler()
        self._textures = {}
        self._vao = mgl.VAO()
        self._vbo = mgl.Buffer("1f", [1.0])

    def load(self):
        """Load the model from the file path."""
        pass


# ------------------------------ #
# .obj


class MTLObjLoader(Loader):
    # ------------------------------ #

    MTL_EXT: str = ".mtl"
    OBJ_EXT: str = ".obj"
    IMG_EXT: list = [".jpg", ".png"]

    def __init__(self, path: str):
        """
        MTL object loader
        - all files should be found in a folder
        - textues + .mtl + .obj all found in root folder
        """
        super().__init__(path)
        # load the path -- find source folder or textures folder
        _dir = os.listdir(path)
        # find certain files
        self._obj = Loader.find_file_ext(path, self.OBJ_EXT)
        # config for mtl file
        self._config = {}
        # results
        self._results = {}

    @property
    def results(self):
        """Get results"""
        return self._results

    @property
    def objects(self):
        """Get all object names"""
        return list(self._results.keys())

    def load(self):
        """Load the mtl + obj file data"""
        # load obj file -- http://web.cse.ohio-state.edu/~shen.94/581/Site/Lab3_files/Labhelp_Obj_parser.htm
        with open(self._obj, "r") as file:
            data = file.read()

        # data
        objects = {}
        current_object = None
        reference = None

        vertices = []
        uvcoords = []
        normals = []

        for line in data.split("\n"):
            if not line or line[0] == "#":
                continue
            # parsing
            words = line.split()
            if words[0] == "mtllib":
                # load mtl file
                self.load_mtl(os.path.join(self._path, " ".join(words[1:])))
            elif words[0] == "o":
                if current_object:
                    # if current_object in objects:
                    #     current_object += "(1)"
                    # what if objects have same name?
                    objects[current_object] = reference
                # make new
                current_object = " ".join(words[1:])
                # new obj -- 0 = vertices, 1 = uv, 2 = normal, 3 = faces
                reference = {
                    "faces": [],
                    "texture": None,
                }
            elif words[0] == "vt":
                vt = tuple(map(float, line.split()[1:]))
                uvcoords.append(vt)
            elif words[0] == "vn":
                vn = tuple(map(float, line.split()[1:]))
                normals.append(vn)
            elif words[0] == "v":
                v = tuple(map(float, line.split()[1:]))
                vertices.append(v)
            elif words[0] == "f":
                # vertex/texture/normal -- texture + normal are optional
                # -1 == does not exist
                face = []
                for x in line.split()[1:]:
                    r = []
                    for i in x.split("/") + [""] * (3 - len(x.split("/"))):
                        if i == "":
                            continue
                        r.append(int(i))
                    face.append(r)
                # check for size
                if len(face) == 4:
                    # 0, 1, 2 || 2, 3, 0
                    # add 2 Face objects to reference in above order
                    reference["faces"].append(Face(face[0], face[1], face[2]))
                    reference["faces"].append(Face(face[2], face[3], face[0]))
                elif len(face) == 3:
                    reference["faces"].append(Face(face[0], face[1], face[2]))
            elif words[0] == "usemtl":
                # use material
                # print(self._textures)
                if words[1] == "none":
                    continue
                reference["texture"] = self._textures[words[1]]
        objects[current_object] = reference

        # iterate thorugh each of the remaeining objects and construct the vertex buffer using the data found in the faces
        for name, data in objects.items():
            # get data
            faces = data["faces"]
            # get texture
            texture = data["texture"]
            # create buffer
            buffer = []
            for face in faces:
                for vertex in face:
                    # get vertex data
                    # print(current_object, vertex, vertices)
                    v = vertices[vertex[0] - 1]
                    vt = uvcoords[vertex[1] - 1]
                    vn = normals[vertex[2] - 1]
                    # add to buffer
                    buffer.extend(v)
                    buffer.extend(vt)
                    buffer.extend(vn)
            # add to results
            vertex_buffer = mgl.Buffer(f"{len(buffer)}f", buffer)
            self._results[name] = Model(vertex_buffer, texture)
        return self._results

    def load_mtl(self, path: str):
        """Load an mtl file"""
        # load mtl file
        with open(path, "r") as file:
            # load data
            data = file.read()
        # split into lines
        current_material = None
        current_data = {}
        for line in data.split("\n"):
            if line.startswith("#"):
                continue
            # split into words
            words = line.split()
            if words[0] == "newmtl":
                # new material
                if current_material:
                    # print(current_data)
                    self._textures[current_material] = self.texture_form_data(
                        current_data
                    )
                current_material = words[1]
                current_data = {}
            elif words[0] == "map_Kd":
                path = os.path.join(self._path, words[1] + ".png")
                # load texture
                texture = mgl.Texture
                current_data["texture"] = mgl.Texture.load_texture(path)
                current_data["path"] = path
            elif words[0] == "Kd":
                # diffuse color
                current_data["diffuse"] = tuple(map(float, words[1:]))
            elif words[0] == "Ka":
                # ambient color
                current_data["ambient"] = tuple(map(float, words[1:]))
            elif words[0] == "Ks":
                # specular color
                current_data["specular"] = tuple(map(float, words[1:]))
            elif words[0] == "Ns":
                # specular exponent
                current_data["specular_exponent"] = float(words[1])
            elif words[0] == "d" or words[0] == "Tr":
                # alpha
                current_data["alpha"] = float(words[1])
        # add last material
        if not current_material == "none":
            self._textures[current_material] = current_data

    def texture_form_data(self, data: dict):
        """Create a texture from data"""
        # create texture
        texture = mgl.Texture(mgl.Texture.load_texture(data["path"]))
        # set texture data
        texture.set_data(data)
        return texture

    def get_object(self, name: str):
        """Get an object by name"""
        return self._results[name]
