# -------------------------------------------------- #
# imports
import pygame
from engine.gamesystem.entity import EntityTypes
from engine.gamesystem import particle
from engine.graphics import animation
from engine.misc import maths, clock
from engine import singleton

from engine.handler.eventhandler import Event, Eventhandler
from engine.handler import statehandler

from scripts import entityext, animationext, singleton as EGLOB, skillext
from scripts.game import state, skillhandler

from scripts.entities import fireball

# -------------------------------------------------- #
animation.load_and_parse_aseprite_animation("assets/sprites/mage.json")


# -------------------------------------------------- #
# mage state handler

class IdleState(state.EntityState):
    def __init__(self, parent):
        super().__init__(Mage.IDLE_STATE, parent)

    def start(self):
        self.parent.aregist[Mage.IDLE_ANIM].f_num = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, Mage.IDLE_ANIM)
        # check for player distance etc
        if self.handler.player_dis < Mage.DETECT_RADIUS:
            self.handler.set_active_state(Mage.ALERT_STATE)
        # also calculate for idle movement


class AlertState(state.EntityState):
    def __init__(self, parent):
        super().__init__(Mage.ALERT_STATE, parent)
        self.countdown = Mage.ALERT_PRECAST_CD

    def start(self):
        # print("alert")
        self.countdown = Mage.ALERT_PRECAST_CD

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, Mage.IDLE_ANIM)

        # case 1: timer counts to 0
        self.countdown -= clock.delta_time
        if self.countdown <= 0:
            # case 1 fulfilled, begin precast
            self.handler.set_active_state(Mage.PRECAST_STATE)
        # case 2: player comes too close
        if self.handler.player_dis < Mage.PREF_DIS:
            # case 2 fulfilled, begin flight
            self.handler.set_active_state(Mage.FLIGHT_STATE)
        # case 3: player goes out of range
        elif self.handler.player_dis > Mage.DETECT_RADIUS:
            # case 3 fulfilled, begin idle
            self.handler.set_active_state(Mage.IDLE_STATE)


class PrecastState(state.EntityState):
    def __init__(self, parent):
        super().__init__(Mage.PRECAST_STATE, parent)

    def start(self):
        # print("starting precast")
        self.parent.aregist[Mage.PRECAST_ANIM].fini = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, Mage.PRECAST_ANIM)

        # case 1: finish precast
        if self.parent.aregist[Mage.PRECAST_ANIM].fini > 0:
            # case 1 fulfilled, begin casting
            self.handler.set_active_state(Mage.CASTING_STATE)
        # case 2: what if casting fails? what if player interrupts?


class CastingState(state.EntityState):
    def __init__(self, parent):
        super().__init__(Mage.CASTING_STATE, parent)
        self.casting_cdr = Mage.DEFAULT_CAST_CD

    def start(self):
        # print("casting spell")
        self.casting_cdr = Mage.DEFAULT_CAST_CD
        # decide on an attack and set casting_cdr depending on attack

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, Mage.CASTING_ANIM)

        self.parent.phandler.create_particle()
        # case 1: finish casting
        self.casting_cdr -= clock.delta_time
        if self.casting_cdr < 0:
            # case 1 fulfilled, begin alert state
            # print("attacking")
            self.handler.set_active_state(Mage.POSTCAST_STATE)


class PostcastState(state.EntityState):
    def __init__(self, parent):
        super().__init__(Mage.POSTCAST_STATE, parent)
        self.cani = Mage.POSTCAST_ANIM
        self.wparticle = False

    def start(self):
        self.cani = Mage.POSTCAST_ANIM
        self.wparticle = False
        self.parent.aregist[Mage.POSTCAST_ANIM].fini = 0

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, self.cani)

        # case 1: finish postcast
        if not self.parent.phandler.ap_count:
            self.wparticle = True
        if self.parent.aregist[Mage.POSTCAST_ANIM].fini > 0:
            if self.wparticle:
                # case 1 fulfilled, begin alrt
                # add finished spell to world
                skill = self.parent.skhandler.get_skill(fireball.SKILL_NAME)
                fire = skill.activate(self.parent, self.parent.atk_phandler)
                self.parent.add_active_attack(fire)
                fire.position = maths.convert_array_to_int(self.parent.rect.center)
                fire.motion = self.parent.player_dis.normalize() * 2
                self.parent.layer.handler.add_entity(fire)
                self.handler.set_active_state(Mage.ALERT_STATE)
        # case 2: interrupted -> backlash


class FlightState(state.EntityState):
    def __init__(self, parent):
        super().__init__(Mage.FLIGHT_STATE, parent)

    def distance_desire_coef(self, dis: float) -> float:
        return 1 / (.05 * dis + 4 / 5)

    def update(self):
        entityext.update_ani_and_hitbox(self.parent, Mage.RUN_ANIM)
        # player is already known to be nearby
        if self.parent.player_dis:
            self.parent.player_dis.normalize()
        self.parent.motion -= self.parent.player_dis * clock.delta_time * self.distance_desire_coef(
            self.handler.player_dis)
        if self.handler.player_dis > Mage.PREF_DIS:
            self.handler.current_state = Mage.ALERT_STATE

        # case 1: player is too close --> go to melee def/atk mode
        if self.handler.player_dis < Mage.DEF_DISTANCE:
            # case 1 fulfilled, begin precast
            self.handler.set_active_state(Mage.PRECAST_STATE)
        # case 2: player leaves zone
        elif self.handler.player_dis > Mage.PREF_DIS:
            # case 2 fulfilled, begin alert state
            self.handler.set_active_state(Mage.ALERT_STATE)


class StateHandler(statehandler.StateHandler):
    def __init__(self, mage):
        super().__init__(Mage.IDLE_STATE)
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

class Mage(entityext.GameEntity):
    TYPE = "Mage"

    # -------------------------------------------------- #
    # animations
    ANIM_CAT = "mage"
    IDLE_ANIM = "idle"
    RUN_ANIM = "run"
    PRECAST_ANIM = "pre_attack"
    CASTING_ANIM = "casting"
    POSTCAST_ANIM = "end_cast"

    # load
    ANIM_CATEGORY = animation.Category.get_category(ANIM_CAT)
    ANIM_CATEGORY.apply_func_to_animations(animationext.handle_handle_position)

    # -------------------------------------------------- #
    # states
    IDLE_STATE = "idle"
    ALERT_STATE = "alert"
    FLIGHT_STATE = "flight"
    PRECAST_STATE = "precast"
    CASTING_STATE = "casting"
    POSTCAST_STATE = "postcast"
    ATTACK_STATE = "firing"

    # -------------------------------------------------- #
    # statistics
    MS = 20
    LC = 0.3

    DETECT_RADIUS = 130
    PREF_DIS = 70
    DEF_DISTANCE = 30

    # cdt
    ALERT_PRECAST_CD = 1.0
    DEFAULT_CAST_CD = 2.3

    # -------------------------------------------------- #
    # signals
    MOVEMENT_SIGNAL = "mage-move"

    # wrappers
    MOVEMENT_WRAPPER = Eventhandler.register_to_signal(MOVEMENT_SIGNAL, lambda x: print(x.name, f"{x.data['x']:.2f}, {x.data['y']:.2f}"))
    # -------------------------------------------------- #
    # buffered objects
    SKILL_TREE = skillhandler.SkillTree(skillext.SkillTreeLoader("assets/skilltree/mage.json"))

    SKILLS = skillhandler.SkillHandler()
    SKILLS.add_skill(fireball.FireBallSkill())

    MOVE_EVENT = Event(MOVEMENT_SIGNAL, {'x': 0, 'y': 0})

    # -------------------------------------------------- #
    def __init__(self):
        super().__init__(Mage.TYPE, 100, 100)
        self.aregist = Mage.ANIM_CATEGORY.create_registry_for_all()
        self.sprite = self.aregist[Mage.IDLE_ANIM].get_frame()
        self.hitbox = self.aregist[Mage.IDLE_ANIM].get_hitbox()
        # distance from player
        self.player_dis = pygame.math.Vector2()

        # state handler
        self.shandler = StateHandler(self)
        # particle handler
        self.phandler = MagicParticleHandler(self)
        self.atk_phandler = fireball.FireParticleHandler(self)
        # skill tree
        self.skhandler = Mage.SKILL_TREE.get_registry(self)

    def update(self):
        self.player_dis.x = EGLOB.PLAYER.rect.centerx - self.rect.centerx
        self.player_dis.y = EGLOB.PLAYER.rect.centery - self.rect.centery
        self.shandler.player_dis = self.player_dis.magnitude()

        self.shandler.update()
        self.layer.world.move_entity(self)

        self.move_to_position()
        self.motion *= Mage.LC

        # output
        Mage.MOVE_EVENT.data['x'] = self.motion.x
        Mage.MOVE_EVENT.data['y'] = self.motion.y
        # self.eventhandler.emit_signal(Mage.MOVE_EVENT)
        # print("mage", self.shandler.current_state)

    def render(self, surface):
        surface.blit(self.sprite if self.motion.x < 0 else pygame.transform.flip(self.sprite, 1, 0),
                     self.get_glob_pos())
        # particle handler
        self.phandler.render(surface)
        self.atk_phandler.render(surface)

    def debug(self, surface):
        super().debug(surface)
        # entity.render_entity_hitbox(self, surface)
        pygame.draw.circle(surface, (255, 0, 0), self.get_glob_cpos(), Mage.DETECT_RADIUS, width=1)
        pygame.draw.circle(surface, (0, 0, 255), self.get_glob_cpos(), Mage.PREF_DIS, width=1)
        pygame.draw.circle(surface, (0, 100, 100), self.get_glob_cpos(), Mage.DEF_DISTANCE, width=1)

    def kill(self):
        super().kill()


class MagicParticleHandler(particle.ParticleHandler):
    SPAWN_RADIUS = Mage.DEF_DISTANCE
    LIFE = 2.0
    FREQ = 30
    COLOR = (255, 0, 100)

    LERP = 0.05

    def __init__(self, parent):
        super().__init__(parent)
        self.set_color(MagicParticleHandler.COLOR)
        self.set_freq(MagicParticleHandler.FREQ)
        self.set_life(MagicParticleHandler.LIFE)
        self.set_create_func(self._create)
        self.set_update_func(self._update)

    def _create(self, _):
        self.p_count += 1
        # calculate x and y
        theta = maths.normalized_random() * 3.14
        x = maths.math.sin(
            theta) * MagicParticleHandler.SPAWN_RADIUS + maths.normalized_random() * 10 + self.parent.rel_hitbox.centerx
        y = maths.math.cos(
            theta) * MagicParticleHandler.SPAWN_RADIUS + maths.normalized_random() * 10 + self.parent.rel_hitbox.centery
        mx = maths.math.sin(theta + 3.14 / 2)
        my = maths.math.cos(theta + 3.14 / 2)
        self.particles[self.p_count] = [self.p_count, x, y, 1, self.start_life, mx, my]

    def _update(self, _, p, surface):
        p[singleton.PARTICLE_LIFE] -= clock.delta_time
        if p[singleton.PARTICLE_LIFE] < 0:
            self.rq.append(p[singleton.PARTICLE_ID])
            return
        # update position
        p[singleton.PARTICLE_MX] = maths.lerp(p[singleton.PARTICLE_MX], 0.0, MagicParticleHandler.LERP)
        p[singleton.PARTICLE_MY] = maths.lerp(p[singleton.PARTICLE_MY], 0.0, MagicParticleHandler.LERP)
        off = pygame.math.Vector2(self.parent.rel_hitbox.centerx - p[singleton.PARTICLE_X],
                                  self.parent.rel_hitbox.centery - p[singleton.PARTICLE_Y])
        off.normalize_ip()
        p[singleton.PARTICLE_MX] += off.x * clock.delta_time
        p[singleton.PARTICLE_MY] += off.y * clock.delta_time

        p[singleton.PARTICLE_X] += p[singleton.PARTICLE_MX]
        p[singleton.PARTICLE_Y] += p[singleton.PARTICLE_MY]
        # render
        pygame.draw.circle(surface, self.color,
                           (p[singleton.PARTICLE_X] + singleton.WORLD_OFFSET_X, p[singleton.PARTICLE_Y] + singleton.WORLD_OFFSET_Y), 1)


# -------------------------------------------------- #
# setup
EntityTypes.register_entity_type(Mage.TYPE, Mage)
