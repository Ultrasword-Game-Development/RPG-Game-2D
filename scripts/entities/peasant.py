# -------------------------------------------------- #
# imports
import pygame
from pygame import math as pgmath, draw as pgdraw

import soragl as SORA
from soragl import physics, base_objects, animation, smath, misc
from soragl import signal, statesystem

from scripts.attacks import short_melee
from scripts.game import skillhandler
from scripts import singleton, skillext

# -------------------------------------------------- #
# peasant 
ANIM_CAT = "assets/sprites/peasant.json"
IDLE_ANIM = "idle"
RUN_ANIM = "run"

animation.Category.load_category(ANIM_CAT)

# -------------------------------------------------- #
# peasant states

IDLE_STATE = "idle"
IDLE_MOVE_STATE = "idle-move"
ALERT_STATE = "alert"
APPROACH_STATE = "approach"
ORBIT_STATE = "orbit"
ATTACK_STATE = "attack"
RUN_STATE = "run"

# -------------------------------------------------- #
# constnats

PLAYER_DISTANCE_NVEC = "player_dis_normvec"
PLAYER_DISTANCE = "player_dis"
PARENT = "parent"

# -------------------------------------------------- #
# statistics
MS = 150
LC = 0.3

DETECT_RADIUS = 80
ATTACK_RANGE = 30
MELEE_ATTACK_RANGE = 25
MAGE_HOVER_DIS = 120

# cdt
ENVIRO_CHECK_TIMER = 2.5
ALERT_DECISION_PAUSE = 0.5
IDLE_MOVE_PAUSE = 3.0

IDLE_MOVE_PERIOD = 1.4
IDLE_MOVE_WAIT = 1.0
ORBIT_ATTACK_WAIT = 1.5
RUN_TIME_PERIOD = 1.5

IDLE_MOVE_MAGE_WEIGHT = 0.6

# -------------------------------------------------- #
# signals

SKILL_TREE = skillhandler.SkillTree(skillext.SkillTreeLoader("assets/skilltree/peasant.json"))

SKILLS = skillhandler.SkillHandler()
SKILLS.add_skill(short_melee.MeleeRangeSkill())

MOVEMENT_SIGNAL = signal.register_signal(signal.SignalRegister("peasant-move"))
# receiver
MOVEMENT_RECEIVER = MOVEMENT_SIGNAL.add_receiver(
    signal.Receiver(lambda data: print(data))
)

# -------------------------------------------------- #
# buffered objects

# -------------------------------------------------- #
# mage state handler

class IdleState(statesystem.State):
    def __init__(self):
        super().__init__(IDLE_STATE)

    def start(self):
        self.handler[PARENT]._current_anim = IDLE_ANIM
        self.handler[PARENT].aregist[IDLE_ANIM].reset()

    def update(self):
        # case 1: player enters detect range
        pass

class AlertState(statesystem.State):
    def __init__(self):
        super().__init__(ALERT_STATE)
        self.countdown = ALERT_PRECAST_CD

    def start(self):
        # print("alert")
        self.handler[PARENT]._current_anim = IDLE_ANIM
        self.countdown = ALERT_PRECAST_CD

    def update(self):
        # print('alert', self.countdown)
        # case 1: timer counts to 0 == then we go attack
        self.countdown -= SORA.DELTA
        if self.countdown <= 0:
            self.handler.current = PRECAST_STATE
        # case 2: player comes too close -- then run away
        if self.handler[PLAYER_DISTANCE] < PREF_DIS:
            self.handler.current = FLIGHT_STATE
        # case 3: player goes out of range
        elif self.handler[PLAYER_DISTANCE] > DETECT_RADIUS:
            self.handler.current = IDLE_STATE

class PrecastState(statesystem.State):
    def __init__(self):
        super().__init__(PRECAST_STATE)

    def start(self):
        self.handler[PARENT].aregist[PRECAST_ANIM].reset()
        self.handler[PARENT]._current_anim = PRECAST_ANIM
        # enable particles
        self.handler[PARENT].ph_magic.enable_particles()

    def update(self):
        # case 1: finish precast
        # print(self.handler[PARENT].aregist[PRECAST_ANIM].finished_loops())
        if self.handler[PARENT].aregist[PRECAST_ANIM].finished_loops() > 0:
            self.handler.current = CASTING_STATE
        # case 2: what if casting fails? what if player interrupts?
        # TODO - code

class CastingState(statesystem.State):
    def __init__(self):
        super().__init__(CASTING_STATE)
        self.casting_cdr = DEFAULT_CAST_CD

    def start(self):
        self.casting_cdr = DEFAULT_CAST_CD
        self.handler[PARENT].ph_magic.enable_particles()
        self.handler[PARENT].aregist[CASTING_ANIM].reset()
        self.handler[PARENT]._current_anim = CASTING_ANIM

    def update(self):
        # print(self.name, self.casting_cdr)
        # case 1: finish casting
        self.casting_cdr -= SORA.DELTA
        if self.casting_cdr < 0:
            self.handler.current = POSTCAST_STATE

class PostcastState(statesystem.State):
    def __init__(self):
        super().__init__(POSTCAST_STATE)
        self.cani = POSTCAST_ANIM

    def start(self):
        self.cani = POSTCAST_ANIM
        # set animation
        self.handler[PARENT]._current_anim = POSTCAST_ANIM
        self.handler[PARENT].aregist[POSTCAST_ANIM].reset()
        # disable particles
        self.handler[PARENT].ph_magic.disable_particles()

    def update(self):
        # case 1: finish postcast -- until no more particles
        # print(self.name, len(self.handler[PARENT].ph_magic))
        if not len(self.handler[PARENT].ph_magic) and self.handler[PARENT].aregist[POSTCAST_ANIM].finished_loops() > 0:
            self.shoot_fireball()
            self.handler.current = ALERT_STATE
        # case 2: interrupted -> backlash
    
    # ---------------------------- #
    def shoot_fireball(self):
        # print("added fireball")
        skill = self.handler[PARENT].skhandler.get_skill(fireball.FB_SKILL_NAME)
        fire = skill.activate(self.handler[PARENT])
        fire.position = self.handler[PARENT].position
        fire.velocity = self.handler[PLAYER_DISTANCE_NVEC] * 2
        self.handler[PARENT].world.add_entity(fire)

class FlightState(statesystem.State):
    def __init__(self):
        super().__init__(FLIGHT_STATE)

    def start(self):
        self.handler[PARENT]._current_anim = RUN_ANIM
        self.handler[PARENT].aregist[RUN_ANIM].reset()

    def update(self):
        # player is already known to be nearby
        self.handler[PARENT].velocity -= self.handler[PLAYER_DISTANCE_NVEC] * SORA.DELTA * self.distance_desire_coef(self.handler[PLAYER_DISTANCE]) * MS
        
        if self.handler[PLAYER_DISTANCE] > PREF_DIS:
            self.handler.current = ALERT_STATE
        # case 1: player is too close --> go to melee def/atk mode
        if self.handler[PLAYER_DISTANCE] < DEF_DISTANCE:
            # case 1 fulfilled, begin precast
            self.handler.current = PRECAST_STATE
        # case 2: player leaves zone
        elif self.handler[PLAYER_DISTANCE] > PREF_DIS:
            # case 2 fulfilled, begin alert state
            self.handler.current = ALERT_STATE

    def distance_desire_coef(self, dis: float) -> float:
        return 1 / (.05 * dis + 4 / 5)

# -------------------------------------------------- #
# peasant

class Peasant(physics.Entity):
    def __init__(self):
        super().__init__()
        # private
        self._current_anim = IDLE_ANIM

        # objects
        self.aregist = animation.Category.get_registries_for_all(ANIM_CAT)
        
        self.c_sprite = base_objects.AnimatedSprite(0, 0, self.aregist[self._current_anim])
        self.c_collision = base_objects.Collision2DComponent()
        self.c_statehandler = statesystem.StateHandler()
        
        # skill tree
        self.skhandler = SKILL_TREE.get_registry(self)
    
    def on_ready(self):
        super().on_ready()
        self.area = (8, 8)
        self.c_statehandler[PARENT] = self
        self.c_statehandler[PLAYER_DISTANCE_NVEC] = pgmath.Vector2()
        self.c_statehandler[PLAYER_DISTANCE] = 0
        
        # add states
        self.c_statehandler.add_state(IdleState())
        self.c_statehandler.add_state(AlertState())
        self.c_statehandler.add_state(PrecastState())
        self.c_statehandler.add_state(CastingState())
        self.c_statehandler.add_state(FlightState())
        self.c_statehandler.add_state(PostcastState())
        self.c_statehandler.current = IDLE_STATE

        # add components
        self.add_component(self.c_sprite)
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(self.c_collision)
        self.add_component(self.c_statehandler)
        self.add_component(base_objects.Script())

    def update(self):
        # testing
        # self.ph_magic.enable_particles()
        # print(self.ph_magic.position)
        self.c_statehandler[PLAYER_DISTANCE_NVEC] = (singleton.PLAYER.position - self.position)
        self.c_statehandler[PLAYER_DISTANCE] = self.c_statehandler[PLAYER_DISTANCE_NVEC].magnitude()
        self.c_statehandler[PLAYER_DISTANCE_NVEC].normalize_ip()
        self.aregist[self._current_anim].update()
        self.c_sprite.registry = self.aregist[self._current_anim]
        self.velocity = smath.v2lerp(self.velocity, (0,0), LC)
        # set sprite flipping
        self.c_sprite.flip = self.velocity.x > 0
        # output
        # MOVEMENT_SIGNAL.emit_signal(velocity=self.velocity, player_distance=self.c_statehandler[PLAYER_DISTANCE])
    
    def script(self):
        # if SORA.DEBUG:
            # pygame.draw.circle(SORA.DEBUGBUFFER, (255, 0, 0), self.position - SORA.OFFSET, DETECT_RADIUS, width=1)
            # pygame.draw.circle(SORA.DEBUGBUFFER, (0, 0, 255), self.position - SORA.OFFSET, PREF_DIS, width=1)
            # pygame.draw.circle(SORA.DEBUGBUFFER, (0, 100, 100), self.position - SORA.OFFSET, DEF_DISTANCE, width=1)

# -------------------------------------------------- #
# particle handler

MG_PARTICLE_FUNC = "mage_particles"

MG_SPAWN_RADIUS = DEF_DISTANCE
MG_LIFE = 2.0
MG_FREQ = 1/30
MG_COLOR = (255, 0, 100)
MG_LERP = 0.05
MG_SPEED = 50

MG_iPOSITION = 0
MG_iVELOCITY = 1
MG_iLIFE = 2
MG_iCOLOR = 3
MG_iID = 4

def mage_particle_create(parent, **kwargs):
    """
    create a magic particle
    - position
    - velocity
    - life
    - color
    - id
    """
    # calcualte x and y
    theta = smath.normalized_random() * 3.14
    # angle rotation + random offset
    x = smath.math.sin(theta) * MG_SPAWN_RADIUS + smath.normalized_random() * 10 + parent.position.x
    y = smath.math.cos(theta) * MG_SPAWN_RADIUS + smath.normalized_random() * 10 + parent.position.y
    # create particle
    mx = smath.math.sin(theta + 3.14/2) * MG_SPEED
    my = smath.math.cos(theta + 3.14/2) * MG_SPEED
    return [pgmath.Vector2(x, y), pgmath.Vector2(mx, my), MG_LIFE, MG_COLOR, parent.get_new_particle_id()]

def mage_particle_update(parent, particle):
    """
    update a magic particle
    """
    particle[MG_iLIFE] -= SORA.DELTA
    if particle[MG_iLIFE] < 0:
        parent.remove_particle(particle)
        return
    # update position
    particle[MG_iVELOCITY] = smath.v2lerp(particle[MG_iVELOCITY], (0, 0), MG_LERP)
    particle[MG_iPOSITION] += particle[MG_iVELOCITY] * SORA.DELTA
    # find offset
    offset = parent.position - particle[MG_iPOSITION]
    # move particle towards center
    particle[MG_iVELOCITY] += offset * SORA.DELTA
    # render the particles
    pgdraw.circle(SORA.FRAMEBUFFER, particle[MG_iCOLOR], particle[MG_iPOSITION] - SORA.OFFSET, 1)

# register particle handler
physics.ParticleHandler.register_particle_setting(MG_PARTICLE_FUNC, mage_particle_create, 
                mage_particle_update, data={"interval": MG_FREQ})
