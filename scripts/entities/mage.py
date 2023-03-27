# -------------------------------------------------- #
# imports
import pygame
from pygame import math as pgmath, draw as pgdraw
import soragl as SORA
from soragl import physics, base_objects, animation, smath, misc
from soragl import signal, statesystem

from scripts.attacks import fireball
from scripts.game import skillhandler
from scripts import singleton, skillext

# -------------------------------------------------- #
# mage 
ANIM_CAT = "assets/sprites/mage.json"
IDLE_ANIM = "idle"
RUN_ANIM = "run"
PRECAST_ANIM = "pre_attack"
CASTING_ANIM = "casting"
POSTCAST_ANIM = "end_cast"

animation.Category.load_category(ANIM_CAT)

# -------------------------------------------------- #
# mage states

IDLE_STATE = "idle"
ALERT_STATE = "alert"
FLIGHT_STATE = "flight"
PRECAST_STATE = "precast"
CASTING_STATE = "casting"
POSTCAST_STATE = "postcast"
ATTACK_STATE = "firing"

# -------------------------------------------------- #
# statistics
MS = 150
LC = 0.1

DETECT_RADIUS = 130
PREF_DIS = 70
DEF_DISTANCE = 30

# cdt
ALERT_PRECAST_CD = 1.0
DEFAULT_CAST_CD = 2.3

# -------------------------------------------------- #
# signals
MOVEMENT_SIGNAL = signal.register_signal(signal.SignalRegister("mage-move"))
# receiver
MOVEMENT_RECEIVER = MOVEMENT_SIGNAL.add_receiver(
    signal.Receiver(lambda data: print(data))
)

# -------------------------------------------------- #
# buffered objects

SKILL_TREE = skillhandler.SkillTree(skillext.SkillTreeLoader("assets/skilltree/mage.json"))

SKILLS = skillhandler.SkillHandler()
SKILLS.add_skill(fireball.FireBallSkill())

# -------------------------------------------------- #
# mage state handler

class IdleState(statesystem.EntityState):
    def __init__(self, parent):
        super().__init__(IDLE_STATE, parent)

    def start(self):
        self.parent.aregist[IDLE_ANIM].f_num = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, IDLE_ANIM)
        # check for player distance etc
        if self.handler.player_dis < DETECT_RADIUS:
            self.handler.set_active_state(ALERT_STATE)
        # also calculate for idle movement

class AlertState(statesystem.EntityState):
    def __init__(self, parent):
        super().__init__(ALERT_STATE, parent)
        self.countdown = ALERT_PRECAST_CD

    def start(self):
        # print("alert")
        self.countdown = ALERT_PRECAST_CD

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, IDLE_ANIM)

        # case 1: timer counts to 0
        self.countdown -= clock.delta_time
        if self.countdown <= 0:
            # case 1 fulfilled, begin precast
            self.handler.set_active_state(PRECAST_STATE)
        # case 2: player comes too close
        if self.handler.player_dis < PREF_DIS:
            # case 2 fulfilled, begin flight
            self.handler.set_active_state(FLIGHT_STATE)
        # case 3: player goes out of range
        elif self.handler.player_dis > DETECT_RADIUS:
            # case 3 fulfilled, begin idle
            self.handler.set_active_state(IDLE_STATE)

class PrecastState(statesystem.EntityState):
    def __init__(self, parent):
        super().__init__(PRECAST_STATE, parent)

    def start(self):
        # print("starting precast")
        self.parent.aregist[PRECAST_ANIM].fini = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, PRECAST_ANIM)

        # case 1: finish precast
        if self.parent.aregist[PRECAST_ANIM].fini > 0:
            # case 1 fulfilled, begin casting
            self.handler.set_active_state(CASTING_STATE)
        # case 2: what if casting fails? what if player interrupts?

class CastingState(statesystem.EntityState):
    def __init__(self, parent):
        super().__init__(CASTING_STATE, parent)
        self.casting_cdr = DEFAULT_CAST_CD

    def start(self):
        # print("casting spell")
        self.casting_cdr = DEFAULT_CAST_CD
        # decide on an attack and set casting_cdr depending on attack

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, CASTING_ANIM)

        self.parent.phandler.create_particle()
        # case 1: finish casting
        self.casting_cdr -= clock.delta_time
        if self.casting_cdr < 0:
            # case 1 fulfilled, begin alert state
            # print("attacking")
            self.handler.set_active_state(POSTCAST_STATE)

class PostcastState(statesystem.EntityState):
    def __init__(self, parent):
        super().__init__(POSTCAST_STATE, parent)
        self.cani = POSTCAST_ANIM
        self.wparticle = False

    def start(self):
        self.cani = POSTCAST_ANIM
        self.wparticle = False
        self.parent.aregist[POSTCAST_ANIM].fini = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, self.cani)

        # case 1: finish postcast
        if not self.parent.phandler.ap_count:
            self.wparticle = True
        if self.parent.aregist[POSTCAST_ANIM].fini > 0:
            if self.wparticle:
                # case 1 fulfilled, begin alrt
                # add finished spell to world
                skill = self.parent.skhandler.get_skill(fireball.FireBallSkill.SKILL_NAME)
                fire = skill.activate(self.parent, self.parent.atk_phandler)
                self.parent.add_active_attack(fire)
                fire.position = maths.convert_array_to_int(self.parent.rect.center)
                fire.motion = self.parent.player_dis.normalize() * 2
                self.parent.layer.handler.add_entity(fire)
                self.handler.set_active_state(ALERT_STATE)
        # case 2: interrupted -> backlash

class FlightState(statesystem.EntityState):
    def __init__(self, parent):
        super().__init__(FLIGHT_STATE, parent)

    def distance_desire_coef(self, dis: float) -> float:
        return 1 / (.05 * dis + 4 / 5)

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, RUN_ANIM)
        # player is already known to be nearby
        if self.parent.player_dis:
            self.parent.player_dis.normalize()
        self.parent.motion -= self.parent.player_dis * clock.delta_time * self.distance_desire_coef(
            self.handler.player_dis)
        if self.handler.player_dis > PREF_DIS:
            self.handler.current_state = ALERT_STATE

        # case 1: player is too close --> go to melee def/atk mode
        if self.handler.player_dis < DEF_DISTANCE:
            # case 1 fulfilled, begin precast
            self.handler.set_active_state(PRECAST_STATE)
        # case 2: player leaves zone
        elif self.handler.player_dis > PREF_DIS:
            # case 2 fulfilled, begin alert state
            self.handler.set_active_state(ALERT_STATE)

class StateHandler(statesystem.StateHandler):
    def __init__(self, mage):
        super().__init__(IDLE_STATE)
        self.mage = mage
        self.player_dis = 0

        # add all necassary states
        self.add_state(IdleState(self.mage))
        self.add_state(AlertState(self.mage))
        self.add_state(PrecastState(self.mage))
        self.add_state(CastingState(self.mage))
        self.add_state(FlightState(self.mage))
        self.add_state(PostcastState(self.mage))

# -------------------------------------------------- #
# mage

class Mage(physics.Entity):
    def __init__(self):
        super().__init__()

        # private
        self._current_anim = IDLE_ANIM

        # objects
        self.aregist = animation.Category.get_registries_for_all(ANIM_CAT)
        
        self.c_sprite = base_objects.AnimatedSprite(0, 0, self.aregist[self._current_anim])
        self.c_collision = base_objects.Collision2DComponent()
        self.c_statehandler = statesystem.StateHandler()
        self.c_statehandler["player_dis"] = pgmath.Vector2()
        
        # particle handler
        self.ph_magic = physics.ParticleHandler(handler_type=ANIM_CAT)
        # skill tree
        self.skhandler = SKILL_TREE.get_registry(self)
    
    def on_ready(self):
        self.area = (8, 8)
        self.c_statehandler.add_state(IdleState(self))
        self.c_statehandler.add_state(AlertState(self))
        self.c_statehandler.add_state(PrecastState(self))
        self.c_statehandler.add_state(CastingState(self))
        self.c_statehandler.add_state(FlightState(self))
        self.c_statehandler.add_state(PostcastState(self))

        # add components
        self.add_component(self.c_sprite)
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(self.c_collision)
        self.add_component(self.c_statehandler)

    def update(self):
        self.c_statehandler["player_dis"] = singleton.PLAYER.position - self.position
        self.aregist[self._current_anim].update()
        self.velocity = smath.v2lerp(self.velocity, (0,0), LC)
        
        # set sprite flipping
        self.c_sprite.flip = self.velocity.x > 0

        # output
        MOVEMENT_SIGNAL.emit_signal(velocity=self.velocity)
    
    def debug(self, surface):
        super().debug(surface)
        # entity.render_entity_hitbox(self, surface)
        pygame.draw.circle(surface, (255, 0, 0), self.get_glob_cpos(), DETECT_RADIUS, width=1)
        pygame.draw.circle(surface, (0, 0, 255), self.get_glob_cpos(), PREF_DIS, width=1)
        pygame.draw.circle(surface, (0, 100, 100), self.get_glob_cpos(), DEF_DISTANCE, width=1)

# -------------------------------------------------- #
# particle handler

MG_PARTICLE_FUNC = "mage_particles"

MG_SPAWN_RADIUS = DEF_DISTANCE
MG_LIFE = 2.0
MG_FREQ = 30
MG_COLOR = (255, 0, 100)
MG_LERP = 0.05

MG_POSITION = 0
MG_VELOCITY = 1
MG_LIFE = 2
MG_COLOR = 3
MG_ID = 4

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
    x = smath.math.sin(theta) * MP_SPAWN_RADIUS + smath.maths.normalized_random() * 10 + parent.position.x
    y = smath.math.cos(theta) * MP_SPAWN_RADIUS + smath.maths.normalized_random() * 10 + parent.position.y
    # create particle
    mx = smath.math.sin(theta + 3.14/2)
    my = smath.math.cos(theta + 3.14/2)
    return [pgmath.Vector2(x, y), pgmath.Vector2(mx, my), MP_LIFE, MP_COLOR, parent.get_new_particle_id()]

def mage_particle_update(parent, particle):
    """
    update a magic particle
    """
    particle[MG_LIFE] -= clock.delta_time
    if particle[MG_LIFE] < 0:
        parent.rq.append(particle[MG_ID])
        return
    # update position
    particle[MG_VELOCITY] = smath.v2lerp(particle[MG_VELOCITY], (0, 0), MG_LERP)
    particle[MG_POSITION] += particle[MG_VELOCITY] * clock.delta_time
    # find offset
    offset = parent.position - particle[MG_POSITION]
    offset.normalize_ip()
    # move particle towards center
    particle[MG_VELOCITY] += offset * clock.delta_time
    # render the particle
    pgdraw.circle(SORA.FRAMEBUFFER, particle[MG_COLOR], particle[MG_POSITION], 1)

# register particle handler
physics.ParticleHandler.register_particle_type(MG_PARTICLE_FUNC, mage_particle_create, mage_particle_update)
