print("Activating physics.py")

import soragl as SORA
import random
import math

from soragl import scene
from pygame import Rect as pRect
from pygame import math as pgmath
from pygame import draw as pgdraw

# ------------------------------------------------------------ #
# global constnats
# ------------------------------------------------------------ #

class World2D:
    RIGHT = pgmath.Vector2(1, 0)
    LEFT = pgmath.Vector2(-1, 0)
    UP = pgmath.Vector2(0, -1)
    DOWN = pgmath.Vector2(0, 1)
    X_AXIS = RIGHT
    Y_AXIS = UP

    GRAVITY = DOWN * 9.8
class World3D:
    X_AXIS = pgmath.Vector3(1, 0, 0)
    Y_AXIS = pgmath.Vector3(0, 1, 0)
    Z_AXIS = pgmath.Vector3(0, 0, 1)

    GRAVITY = Y_AXIS * -9.8
    UP = Y_AXIS



# ------------------------------------------------------------ #
# create a base entity class using the entity system
# ------------------------------------------------------------ #

class Entity:
    ENTITY_COUNT = 0

    def __init__(self):
        # defined after register
        self.world = None
        self.scene = None
        self.handler = None

        # private
        self._components = {}
        self._alive = True
        Entity.ENTITY_COUNT += 1
        self._entity_id = Entity.ENTITY_COUNT
        self._projected_position = pgmath.Vector2()
        self._position = pgmath.Vector2()
        self._velocity = pgmath.Vector2()

        # public
        self.c_chunk = [0, 0]
        self.rect = pRect(0, 0, 0, 0)
        self.static = False

    # whenever components are added -- the world must be queried --> so that cache can be updated
    def on_ready(self):
        """When Entity is ready -- called at end of every update loop by world -- if new entity"""
        # print(self)
        pass

    #=== components
    @property
    def components(self) -> dict:
        """Components property"""
        return self._components
    
    def add_component(self, component) -> "Component":
        """Add a component to the entity"""
        self.world.add_component(self, component)
        return component
    
    def remove_component(self, component):
        """Remove a component from the entity"""
        if component in self._components:
            self.world.remove_component(self, component)
    
    def get_component_from_hash(self, comp_class_hash: int):
        """Get a component from the entity"""
        if comp_class_hash in self._components:
            return self._components[comp_class_hash]
        return None
    
    def get_component(self, comp_class):
        """Get a component from the entity"""
        return self.get_component_from_hash(hash(comp_class))

    def entity_has_component(self, comp_class):
        """Check if an entity has a component"""
        return hash(comp_class) in self._components

    #=== default functions
    def update(self):
        """Default update function"""
        pass

    def kill(self):
        """Kill the entity"""
        self._alive = False

    #=== values / setters / getters
    @property
    def area(self):
        """Get the area"""
        return (self.rect.w, self.rect.h)
    
    @area.setter
    def area(self, new_area: tuple):
        """set a new area"""
        if len(new_area) != 2:
            raise NotImplementedError(f"The area {new_area} is not supported yet! {__file__} {__package__}")
        self.rect.w, self.rect.h= new_area
    
    @property
    def position(self):
        """Position property"""
        return self._position
    
    @position.setter
    def position(self, new_position):
        """Set the position for the entity"""
        self._position.x = new_position[0]
        self._position.y = new_position[1]
    
    @property
    def velocity(self):
        """Velocity property"""
        return self._velocity
    
    @velocity.setter
    def velocity(self, new_velocity):
        """Set the velocity for the entity"""
        self._velocity.x = new_velocity[0]
        self._velocity.y = new_velocity[1]

    #=== standard overloads
    def __eq__(self, o):
        """Overload the == operator"""
        return id(self) == id(o)
    
    def __hash__(self):
        """Overload the hash operator"""
        return self._entity_id


# ------------------------------------------------------------ #
# SAT - check if colliding objects
# ------------------------------------------------------------ #
# checking for collisions

"""
SAT code
- to be used when implementing box2d + movement + polygonal objects in game!
TODO:
- figure out how to do the above :)
"""

def is_separated(shape1, shape2, axis: pgmath.Vector2) -> bool:
    """Return True if the shapes are separated along the given axis"""
    proj1 = [axis.dot(vertex) for vertex in shape1]
    proj2 = [axis.dot(vertex) for vertex in shape2]
    min_proj1, max_proj1 = min(proj1), max(proj1)
    min_proj2, max_proj2 = min(proj2), max(proj2)
    return max_proj1 < min_proj2 or min_proj1 > max_proj2

def overlap_general(shape1_, shape2_) -> bool:
    """Check if two objects overlap -- axis not used"""
    shape1 = list(shape1_.get_vertices())
    shape2 = list(shape2_.get_vertices())
    # TODO: perhaps integrate the AABB for none AABB shapes

    # Test all the normals (edge directions) of shape1
    for i in range(len(shape1)):
        edge = shape1[i] - shape1[i-1]
        axis = pgmath.Vector2(-edge.y, edge.x).normalize()
        if is_separated(shape1, shape2, axis):
            return False

    # Test all the normals (edge directions) of shape2
    for i in range(len(shape2)):
        edge = shape2[i] - shape2[i-1]
        axis = pgmath.Vector2(-edge.y, edge.x).normalize()
        if is_separated(shape1, shape2, axis):
            return False

    # If no separations were found, the shapes are intersecting
    return True


# ------------------------------------------------------------ #
# particle handling + physics
# ------------------------------------------------------------ #

class ParticleHandler(Entity):
    # ------------------------------ #
    # functions for updating + creating particles

    CREATE = {}
    UPDATE = {}
    TIMER_FUNC = {}

    DEFAULT_CREATE = "default_create"
    DEFAULT_UPDATE = "default_update"
    DEFAULT_TIMER = "default_timer"

    @classmethod
    def register_create_function(cls, name, func):
        """Register a create function"""
        cls.CREATE[name] = func

    @classmethod
    def register_update_function(cls, name, func):
        """Register an update function"""
        cls.UPDATE[name] = func

    @classmethod
    def register_timer_function(cls, name, func):
        """Register a timer function"""
        cls.TIMER_FUNC[name] = func
    
    @classmethod
    def get_create_function(cls, name):
        """Get a create function"""
        return cls.CREATE[name] if name in cls.CREATE else cls.CREATE[cls.DEFAULT_CREATE]
    
    @classmethod
    def get_update_function(cls, name):
        """Get an update fucntion"""
        return cls.UPDATE[name] if name in cls.UPDATE else cls.UPDATE[cls.DEFAULT_UPDATE]
    
    @classmethod
    def get_create_timer_funcion(cls, name):
        """Get a timer function"""
        return cls.TIMER_FUNC[name] if name in cls.TIMER_FUNC else cls.TIMER_FUNC[cls.DEFAULT_TIMER]
    
    # ------------------------------ #

    def __init__(self, args: dict = {}, max_particles: int = 100, create_func: str = None, update_func: str = None, create_timer_func: str = None):
        super().__init__()
        # private
        self._particles = {}
        self._particle_count = 0
        self._max_particles = max_particles
        self._data = {
            "interval": 0.1
        }
        self._timer = 0
        self._remove = []
        self.args = args

        # public
        self._function_data = [create_func, update_func, create_timer_func]
        self.create_timer_func = ParticleHandler.get_create_timer_funcion(name=create_timer_func)
        self.create_func = ParticleHandler.get_create_function(name=create_func)
        self.update_func = ParticleHandler.get_update_function(name=update_func)
    
    def get_new_particle_id(self):
        """Get a new particle id"""
        self._particle_count += 1
        return self._particle_count

    @property
    def data(self):
        """Get the data for the particle handler"""
        return self._data

    def __getitem__(self, name):
        """Get a piece of data"""
        return self._data[name]
    
    def __setitem__(self, name, value):
        """Set a piece of data"""
        self._data[name] = value
    
    def remove_particle(self, particle):
        """Remove a particle"""
        self._remove.append(particle[-1])

    def update(self):
        """Update the Particle Handler"""
        # print(self._function_data)
        self.create_timer_func(self)
        for particle in self._particles.values():
            self.update_func(self, particle)
        # remove timer
        for i in self._remove:
            del self._particles[i]
        # self._particle_count -= len(self._remove) # when removing particles bad things happen
        self._remove.clear()


# ------------------------------ #
# default for circle particles
# attribs = [pos, vel, radius, color, life]
# create function
def _default_create(parent, **kwargs):
    """Default create function for particles"""
    return [parent.position.xy, 
            kwargs["vel"] if "vel" in kwargs else pgmath.Vector2(random.random()-0.5, -5),
            kwargs["radius"] if "radius" in kwargs else 2, 
            kwargs["color"] if "color" in kwargs else (0, 0, 255),
            kwargs["life"] if "life" in kwargs else 1.0,
            parent.get_new_particle_id()]

# update function
def _default_update(parent, particle):
    """Default update function for particles"""
    # gravity
    particle[1] += World2D.GRAVITY * SORA.DELTA
    particle[4] -= SORA.DELTA
    if particle[4] <= 0:
        parent.remove_particle(particle)
        return
    # move
    particle[0] += particle[1]
    # render
    pgdraw.circle(SORA.FRAMEBUFFER, particle[3], particle[0], particle[2]) #, 1)

# timer function
def _default_timer(parent):
    """Default timer function for particles"""
    parent._timer += SORA.DELTA
    if parent._timer >= parent._data["interval"]:
        # print(parent._function_data)
        parent._timer = 0
        particle = parent.create_func(parent, **parent.args)
        # print("created particle")
        parent._particles[particle[-1]] = particle
        # print(parent._particle_count)

# update function
ParticleHandler.register_create_function(ParticleHandler.DEFAULT_CREATE, _default_create)
ParticleHandler.register_update_function(ParticleHandler.DEFAULT_UPDATE, _default_update)
ParticleHandler.register_timer_function(ParticleHandler.DEFAULT_TIMER, _default_timer)

