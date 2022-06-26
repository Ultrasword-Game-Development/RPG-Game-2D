import time


FPS = 0
delta_time = 0
start_time = 0
end_time = 0
wait_time = 0
frame_time = 0


def start(fps=30):
    """Start clock"""
    global delta_time, start_time, end_time, frame_time, FPS
    FPS = fps
    frame_time = 1/fps
    delta_time = 0
    start_time = time.time()
    end_time = start_time


def update():
    """Update clock and delta time"""
    global delta_time, start_time, end_time, wait_time, frame_time
    end_time = time.time()
    delta_time = end_time - start_time
    if delta_time < frame_time:
        wait_time = frame_time - delta_time
        time.sleep(wait_time)
        delta_time = frame_time
    start_time = time.time()


# TODO - create a timer object
class Timer:
    def __init__(self, wait_time):
        self.st = 0
        self.wait_time = wait_time
        self.changed = False

    def update(self, dt):
        self.st += dt
        if self.st > self.wait_time:
            self.st = 0
            self.changed = True
        
    def is_changed(self):
        return self.changed


