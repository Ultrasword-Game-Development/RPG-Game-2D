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
    TOPRIGHT = RIGHT.rotate(45)
    TOPLEFT = RIGHT.rotate(135)
    BOTLEFT = RIGHT.rotate(225)
    BOTRIGHT = RIGHT.rotate(315)
    X_AXIS = RIGHT
    Y_AXIS = UP
    GRAVITY = DOWN * 9.8 * 10

class World3D:
    X_AXIS = pgmath.Vector3(1, 0, 0)
    Y_AXIS = pgmath.Vector3(0, 1, 0)
    Z_AXIS = pgmath.Vector3(0, 0, 1)

    GRAVITY = Y_AXIS * -9.8 * 10
    UP = Y_AXIS

# ------------------------------------------------------------ #
# create a base entity class using the entity system
# ------------------------------------------------------------ #

class Entity:
    ENTITY_COUNT = 0

    def __init__(self, name:str=None):
        self.name = f"entity{Entity.ENTITY_COUNT}" if not name else name
        # defined after register
        self.world = None
        self.scene = None
        self.handler = None

        # private
        self._components = {}
        self._linked_entities = [] # links for linked entities
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
        # add to required chunk
        self.c_chunk[0] = self.position.x // self.world._options['chunkpixw']
        self.c_chunk[1] = self.position.y // self.world._options['chunkpixh']

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

    def debug(self):
        """Debug render for entity objects"""
        pass

    def kill(self):
        """Kill the entity == world removes all linked entities"""
        self.world.remove_entity(self)

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
        self.rect.w, self.rect.h = new_area
    
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

    #=== links -- between entiites
    @property
    def links(self) -> list:
        """Links property"""
        return self._links
    
    def add_link(self, entity):
        """Add a link to the entity"""
        self._linked_entities.append(entity)
        self.world.add_entity(entity)
        return entity
    
    def remove_link(self, entity):
        """Remove a link from the entity"""
        if entity in self._linked_entities:
            self._linked_entities.remove(entity)

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

    SETTINGS = {}

    DEFAULT_SETTING = "default"
    DEFAULT_CREATE = "default"
    DEFAULT_UPDATE = "default"
    DEFAULT_TIMER = "default"

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
    
    @classmethod
    def register_particle_setting(cls, name, create_func, update_func, timer_func=None, data:dict={}):
        """Register a particle type"""
        cls.register_create_function(name, create_func)
        cls.register_update_function(name, update_func)
        if not timer_func:
            timer_func = _default_timer
        cls.register_timer_function(name, timer_func)
        # register the setting
        cls.SETTINGS[name] = {
            "create_func": create_func,
            "update_func": update_func,
            "timer_func": timer_func,
            "data": data
        }
    
    @classmethod
    def instance_particle_setting(cls, name):
        """Instance a particle setting"""
        if name in cls.SETTINGS:
            return cls.SETTINGS[name]
        return cls.instance_particle_setting(cls.DEFAULT_SETTING)

    # ------------------------------ #
    # class

    def __init__(self, args: dict = {}, max_particles: int = 100, create_func: str = None, update_func: str = None, create_timer_func: str = None, handler_type: str = None):
        super().__init__()
        if handler_type:
            create_func = handler_type if handler_type in self.CREATE else self.DEFAULT_CREATE
            update_func = handler_type if handler_type in self.UPDATE else self.DEFAULT_UPDATE
            create_timer_func = handler_type if handler_type in self.TIMER_FUNC else self.DEFAULT_TIMER
        # private
        self._create = True
        self._particles = {}
        self._particle_count = 0
        self._total_particles = 0
        self._max_particles = max_particles
        self._data = {
            "interval": 0.1
        }
        self.args = args
        self._timer = 0
        self._remove = []
        self._instant_death = False

        # public
        self._function_data = [create_func, update_func, create_timer_func]
        self._create_timer_func = ParticleHandler.get_create_timer_funcion(name=create_timer_func)
        self._create_func = ParticleHandler.get_create_function(name=create_func)
        self._update_func = ParticleHandler.get_update_function(name=update_func)
    
    def get_new_particle_id(self):
        """Get a new particle id"""
        self._particle_count += 1
        self._total_particles += 1
        return self._particle_count

    # ------------------------------ #
    @property
    def data(self):
        """Get the data for the particle handler"""
        return self._data

    @property
    def create_func(self):
        """Get the create function"""
        return self._create_func
    
    @create_func.setter
    def create_func(self, value):
        """Set the create function"""
        self._function_data[0] = value
        self._create_func = ParticleHandler.get_create_function(name=value)
    
    @property
    def update_func(self):
        """Get the update function"""
        return self._update_func
    
    @update_func.setter
    def update_func(self, value):
        """Set the update function"""
        self._function_data[1] = value
        self._update_func = ParticleHandler.get_update_function(name=value)

    @property
    def create_timer_func(self):
        """Get the timer function"""
        return self._create_timer_func

    @create_timer_func.setter
    def create_timer_func(self, value):
        """Set the timer function"""
        self._function_data[2] = value
        self._create_timer_func = ParticleHandler.get_create_timer_funcion(name=value)

    @property
    def instant_death(self):
        """Get the instant death state"""
        return self._instant_death
    
    @instant_death.setter
    def instant_death(self, value):
        """Set the instant death state"""
        self._instant_death = value

    # ------------------------------ #
    def __getitem__(self, name):
        """Get a piece of data"""
        return self._data[name]
    
    def __setitem__(self, name, value):
        """Set a piece of data"""
        self._data[name] = value
    
    def __len__(self):
        """Get the number of particles"""
        return self._total_particles

    def remove_particle(self, particle):
        """Remove a particle"""
        self._total_particles -= 1
        self._remove.append(particle[-1])

    def disable_particles(self):
        """Disable particles"""
        self._create = False
    
    def enable_particles(self):
        """Enable particles"""
        self._create = True

    # ------------------------------ #
    def update(self):
        """Update the Particle Handler"""
        # print(self._function_data)
        if self._create: self._create_timer_func(self, **self.args)
        for particle in self._particles.values():
            self._update_func(self, particle)
        # remove timer
        for i in self._remove:
            del self._particles[i]
        # self._particle_count -= len(self._remove) # when removing particles bad things happen
        self._remove.clear()

    def kill(self):
        """Kill the particle handler"""
        if self._instant_death: 
            return super().kill()
        # kill all particles
        self.disable_particles()
        if not len(self):
            return super().kill()


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
def _default_timer(parent, **kwargs):
    """Default timer function for particles"""
    parent._timer += SORA.DELTA
    if parent._timer >= parent._data["interval"]:
        # print(parent._function_data)
        parent._timer = 0
        particle = parent.create_func(parent, **parent.args)
        # print("created particle")
        parent._particles[particle[-1]] = particle
        # print(parent._particle_count)

# REGISTER default function
ParticleHandler.register_particle_setting(ParticleHandler.DEFAULT_SETTING, _default_create, _default_update, _default_timer)
