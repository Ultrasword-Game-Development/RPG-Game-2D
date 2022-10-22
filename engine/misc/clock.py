import time
from pygame.time import Clock

PG_CLOCK: Clock = Clock()

FPS: float = 0
delta_time: float = 0
start_time: float = 0
end_time: float = 0
wait_time: float = 0
frame_time: float = 0
run_time: float = 0

engine_start_time: float = time.time()
engine_uptime: float = 0


def start(fps=30):
    """Start clock"""
    global delta_time, start_time, end_time, frame_time, FPS
    FPS = fps
    frame_time = 1/fps
    delta_time = 0
    start_time = time.time()
    end_time = start_time
    print(f"[Engine Initialization Time] Finished in {get_engine_uptime():.2f}s!")


def update():
    """Update clock and delta time"""
    global delta_time, start_time, end_time, frame_time, run_time, FPS, PG_CLOCK
    PG_CLOCK.tick(FPS)
    end_time = time.time()
    delta_time = end_time - start_time
    start_time = time.time()
    run_time += delta_time


def get_engine_uptime() -> float:
    """Get engine uptime"""
    global engine_start_time, engine_uptime
    engine_uptime = time.time() - engine_start_time
    return engine_uptime


# TODO - create a timer object
class Timer:
    def __init__(self, wait_time: float):
        self.st: float = 0
        self.wait_time: float = wait_time
        self.changed: bool = False

    def update(self) -> None:
        self.st += delta_time
        if self.st > self.wait_time:
            self.st = 0
            self.changed = True



