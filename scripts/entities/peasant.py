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
APPROACH_STATE = "approach"
ORBIT_STATE = "orbit"
ATTACK_STATE = "attack"
RUN_STATE = "run"

# -------------------------------------------------- #
# constnats

PLAYER_DISTANCE_NVEC = "player_dis_normvec"
PLAYER_DISTANCE = "player_dis"
PARENT = "parent"
MAGE_HOST = "mage_host"

# -------------------------------------------------- #
# statistics
MS = 250
IDLE_MS = 150
LC = 0.3

DETECT_RADIUS = 40
ATTACK_RANGE = 25
MELEE_ATTACK_RANGE = 25
MAGE_HOVER_DIS = 120

PEASANT_AVOID_DIS = 35
PEASANT_AVOID_COEF = 0.3

TARGET_DISTANCE_ERROR_COEF = 0.1
TARGET_DISTANCE_ERROR = 15

IDLE_MOVE_MAGE_ERROR = 0.4
IDLE_MOVE_MAGE_WEIGHT = 0.6

# cdt
ENVIRO_CHECK_TIMER = 5
ALERT_DECISION_PAUSE = 0.5
IDLE_MOVE_PAUSE = 3.0

IDLE_MOVE_PERIOD = 4.0
IDLE_MOVE_WAIT = 1.0
ORBIT_ATTACK_WAIT = 1.5
RUN_TIME_PERIOD = 1.5


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
# mage state handler

class IdleState(statesystem.State):
    def __init__(self):
        super().__init__(IDLE_STATE)
        self._idle_timer = misc.Timer(IDLE_MOVE_PAUSE)
        self._idle_receiver = self._idle_timer.on_finish(signal.Receiver(self.on_timer_finish))

    def start(self):
        self.handler[PARENT]._current_anim = IDLE_ANIM
        self.handler[PARENT].aregist[IDLE_ANIM].reset()
        self._idle_timer.reset_timer()
        self._idle_timer.start()

    def update(self):
        # case 1: player enters detect range
        if self.handler[PLAYER_DISTANCE] < DETECT_RADIUS:
            self.handler.current = APPROACH_STATE
        
    def end(self):
        self._idle_timer.stop()
        
    def on_timer_finish(self, data: dict):
        """Called when the timer finishes"""
        self.handler.current = IDLE_MOVE_STATE


class IdleMoveState(statesystem.State):
    def __init__(self):
        super().__init__(IDLE_MOVE_STATE)
        self._move_timer = misc.Timer(IDLE_MOVE_PERIOD)
        self._wait_timer = misc.Timer(IDLE_MOVE_WAIT)
        self._move_receiver = self._move_timer.on_finish(signal.Receiver(self.on_move_finish))
        self._wait_receiver = self._wait_timer.on_finish(signal.Receiver(self.on_wait_finish))
        # movement direction
        self._direction = smath.normalized_random_vec2()

    def start(self):
        self.handler[PARENT]._current_anim = RUN_ANIM
        self.handler[PARENT].aregist[RUN_ANIM].reset()
        self._move_timer.reset_timer()
        self._wait_timer.reset_timer()
        self._wait_timer.start()
    
    def update(self):
        # case 1: player is in range
        if self.handler[PLAYER_DISTANCE] < DETECT_RADIUS:
            self.handler.current = APPROACH_STATE
        # print(self._wait_timer.finished_loops)
        if self._move_timer.active:
            # calculate movement vector -- idle motion
            self.handler[PARENT].velocity += self._direction * IDLE_MS * SORA.DELTA
    
    def end(self):
        self._move_timer.stop()

    def on_move_finish(self, data: dict):
        """Called when the move timer finishes"""
        # case 2: movement finishes
        self.handler.current = IDLE_STATE
        if not self.handler[MAGE_HOST]:
            self._direction = smath.normalized_random_vec2()
        else:
            self._direction = smath.weighted_random_vec2(IDLE_MOVE_MAGE_WEIGHT, 
                        (self.handler[MAGE_HOST].position - self.position).normalize()
                        , IDLE_MOVE_MAGE_ERROR)
        # print(self._direction)

    def on_wait_finish(self, data: dict):
        """Called when the wait timer finishes"""
        # case 3: wait finishes
        self._wait_timer.stop()
        self._move_timer.start()


class ApproachState(statesystem.State):
    def __init__(self):
        super().__init__(APPROACH_STATE)

    def start(self):
        self.handler[PARENT]._current_anim = RUN_ANIM
        self.handler[PARENT].aregist[RUN_ANIM].reset()
    
    def update(self):
        # move towards player
        self.handler[PARENT].velocity += self.handler[PLAYER_DISTANCE_NVEC] * MS * SORA.DELTA
        # case 1: player leaves range
        if self.handler[PLAYER_DISTANCE] > DETECT_RADIUS:
            self.handler.current = IDLE_STATE
        # case 2: player enters attack range
        elif self.handler[PLAYER_DISTANCE] < ATTACK_RANGE:
            self.handler.current = ORBIT_STATE
        # case 3: peasant leaves the mage radius
        elif self.handler[MAGE_HOST] and (self.handler[MAGE_HOST].position - self.handler[PARENT].position).magnitude() > MAGE_HOVER_DIS:
            self.handler.current = RUN_STATE


class OrbitState(statesystem.State):
    def __init__(self):
        super().__init__(ORBIT_STATE)
        self._attack_timer = misc.Timer(ORBIT_ATTACK_WAIT)
        self._attack_receiver = self._attack_timer.on_finish(signal.Receiver(self.on_attack_finish))
    
    def start(self):
        self.handler[PARENT]._current_anim = RUN_ANIM
        self.handler[PARENT].aregist[RUN_ANIM].reset()
        self._attack_timer.reset_timer()
        self._attack_timer.start()
    
    def update(self):
        # case 1: player leaves range
        if self.handler[PLAYER_DISTANCE] > DETECT_RADIUS:
            self._attack_timer.stop()
            # do a bit of randomized checking
            if smath.normalized_random() < TARGET_DISTANCE_ERROR_COEF:
                self.handler.current = IDLE_STATE
        # case 2: player is in attack range -- attack timer
        if not self._attack_timer.active:
            self._attack_timer.start()
        # calculate movement -- including avoiding other peasants
        self.handle_movement()

    def end(self):
        self._attack_timer.stop()
    
    def on_attack_finish(self, data: dict):
        """Called when the attack timer finishes"""
        # case 3: attack timer finishes
        self.handler.current = RUN_STATE
        # add an attack particle to the world
        self.handler[PARENT].velocity *= 0
        skill = SKILL_TREE.get_skill(short_melee.MR_SKILL_NAME)
        attack = skill.activate(self.handler[PARENT])
        attack.position = self.handler[PARENT].position
        attack.velocity = self.handler[PLAYER_DISTANCE_NVEC] * 3
        self.handler[PARENT].world.add_entity(attack)

    def handle_movement(self):
        """Handles movement for the peasant"""
        # calculate original movement vector from entity to player
        move_vec = self.handler[PLAYER_DISTANCE_NVEC] * (self.handler[PLAYER_DISTANCE] - ATTACK_RANGE)
        # calculate avoidance vector
        avoidance_vec = pgmath.Vector2(0.0000001, 0)
        for entity in self.handler[PARENT].world.iter_active_entities_filter_entity_exclude_self(self.handler[PARENT], self):
            # check if within detection range otherwise waste of computational power
            dis = (entity.position - self.handler[PARENT].position).magnitude()
            if dis > PEASANT_AVOID_DIS:
                continue
            # calculate avoidance vector
            avoidance_vec += (self.handler[PARENT].position - entity.position) * (PEASANT_AVOID_DIS - dis)
        avoidance_vec.normalize_ip()
        # calculate final movement vector
        self.handler[PARENT].velocity += (move_vec + avoidance_vec * PEASANT_AVOID_COEF) * SORA.DELTA


class RunState(statesystem.State):
    def __init__(self):
        super().__init__(RUN_STATE)
        self._run_timer = misc.Timer(RUN_TIME_PERIOD)
        self._run_timer_receiver = self._run_timer.on_finish(signal.Receiver(self.on_finish_running))

    def start(self):
        self.handler[PARENT]._current_anim = RUN_ANIM
        self.handler[PARENT].aregist[RUN_ANIM].reset()
        self._run_timer.reset_timer()
        self._run_timer.start()

    def update(self):
        # case 1: has a nearby mage character
        if self.handler[MAGE_HOST]:
            direction = (self.handler[MAGE_HOST].position - self.handler[PARENT].position).normalize()
            self.handler[PARENT].velocity -= direction * MS * SORA.DELTA

    def end(self):
        self._run_timer.stop()

    def on_finish_running(self, data: dict):
        """When the timer finishes"""
        self.handler.current = IDLE_STATE


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
        # timer object for mage detection
        self._mage_detection_timer = misc.Timer(ENVIRO_CHECK_TIMER, True)
        self._mage_detection_receiver = self._mage_detection_timer.on_finish(signal.Receiver(self.on_mage_detection_timer_finish))
        
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
        self.c_statehandler.add_state(IdleMoveState())
        self.c_statehandler.add_state(ApproachState())
        self.c_statehandler.add_state(OrbitState())
        self.c_statehandler.add_state(RunState())
        self.c_statehandler.current = IDLE_STATE

        # state timers
        self._mage_detection_timer.start()
        self.on_mage_detection_timer_finish(None)

        # add components
        self.add_component(self.c_sprite)
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(self.c_collision)
        self.add_component(self.c_statehandler)
        self.add_component(base_objects.Script(self.script))

    def update(self):
        # testing
        # self.ph_magic.enable_particles()
        # print(self.c_statehandler.current)
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
        # print(self.velocity)
        if SORA.DEBUG:
            pgdraw.circle(SORA.DEBUGBUFFER, (100, 0, 0), self.position - SORA.OFFSET, DETECT_RADIUS, width=1)
            pgdraw.circle(SORA.DEBUGBUFFER, (0, 0, 100), self.position - SORA.OFFSET, ATTACK_RANGE, width=1)
            pgdraw.circle(SORA.DEBUGBUFFER, (255, 255, 0), self.position - SORA.OFFSET, MAGE_HOVER_DIS, width=1)
            pgdraw.line(SORA.DEBUGBUFFER, (255, 0, 0), self.position - SORA.OFFSET, self.position - SORA.OFFSET + (self.velocity.normalize() if self.velocity else pgmath.Vector2(0.0001, 0)) * 5, width=1)

    def on_mage_detection_timer_finish(self, data: dict):
        self.c_statehandler[MAGE_HOST] = None
        # check if there are mages in range
        for entity in self.world.iter_active_entities():
            if hash(entity) == singleton.T_MAGE:
                if entity.c_collision.get_distance(self.c_collision) < MAGE_HOVER_DIS:
                    # select entity as nearby_mage
                    self.c_statehandler[MAGE_HOST] = entity
                    break


# -------------------------------------------------- #
# particle handler

