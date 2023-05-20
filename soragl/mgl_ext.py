import soragl
from soragl import mgl, misc

# -------------------------------------------------------------- #

BATCH_OBJECT_VERTEX_COUNT = 4


class BatchRenderer:
    def __init__(self, shader_path: str, _type: str, object_count: int, dynamic: bool = False, 
                object_vertex_count: int = BATCH_OBJECT_VERTEX_COUNT):
        """
        BatchRenderer class
        - all for 4 VERTEX shapes
        """
        self._dynamic = dynamic
        self._type = _type
        self._object_count = object_count
        self._object_vertex_count = object_vertex_count
        # creating objects
        # creating them now because we can just update data from them afterwards
        self._ram_vbuffer = mgl.Buffer(f"{self._object_count * self._object_vertex_count}{self._type}", [0.0 for i in range(self._object_count * self._object_vertex_count)], dynamic=dynamic)
        # TODO - find a way to generate for MULTIPLE vertices objects (not 6)
        self._ram_ibuffer = mgl.Buffer(f"{6 * self._object_count}i", misc.n_generate_index_iteration(self._object_count), dynamic=dynamic)
        self._vao = mgl.VAO(shader_path=shader_path)
        # texture handling object
        self._texhandler = mgl.TextureHandler()
    
    def create(self):
        """Create the data buffers and vao"""
        if not self._vao.attributes:
            raise ValueError("No attributes found in VAO (batch renderer)")
        self.upload_buffers()
        self._vao.create_structure(self._ram_vbuffer, self._ram_ibuffer)
    
    def upload_buffers(self):
        """Update the data buffers"""
        # rewrite the entire buffer
        self._ram_vbuffer.update_buffer()
        self._ram_ibuffer.update_buffer()




