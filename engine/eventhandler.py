from collections import deque
from dataclasses import dataclass


"""
Event handler system

- you have the event registered into a dict
- each event will have an id - integer
- when an event is announced, every registered entity will recieve the command and run respective functions
- ggs

"""

events = deque()

def add_event(event_data_block):
    """Append events to the events deque"""
    events.append(event_data_block)


def update_events():
    """Update all events with registered objects"""
    if events:
        for event in events:
            call_event(event.eid, event.data)
        events.clear()


REGISTERED_EVENTS = {} # a eid and event pair
REGISTERED_OBJECTS = {} # a eid and dict(object obejct) pair


EVENT_ID_COUNT = 0
FUNC_REG_ID = 0


def register_event(eid: int):
    """Register an event ID - just an integer value"""
    global REGISTERED_EVENTS, REGISTERED_OBJECTS, EVENT_ID_COUNT
    # create registries within the dictionaries
    REGISTERED_EVENTS[eid] = EventRegistry(eid)

    EVENT_ID_COUNT += 1
    REGISTERED_EVENTS[eid].eid = EVENT_ID_COUNT
    REGISTERED_OBJECTS[eid] = {}
    return REGISTERED_EVENTS[eid]


def register_func_to_event(eid, func) -> int:
    """Register a function/object to an event"""
    global REGISTERED_OBJECTS, FUNC_REG_ID
    # if not registered, register the event
    if REGISTERED_OBJECTS.get(eid) == None: 
        raise RegistryNotFound(eid)
    # increment
    FUNC_REG_ID += 1
    # register the event now
    REGISTERED_OBJECTS[eid][FUNC_REG_ID] = func
    return FUNC_REG_ID


def remove_func_id(id):
    """remove a func id"""
    global REGISTERED_OBJECTS
    for eid, data in REGISTERED_OBJECTS.items():
        if id in data:
            data.pop(id)


def call_event(eid, data) -> None:
    """
    Call all functions registered into the eid
    - given the EID
    - data: dict
    """
    global REGISTERED_OBJECTS, REGISTERED_EVENTS
    for e, func in REGISTERED_OBJECTS[eid].items():
        # registered objects
        func(data)


@dataclass
class EventDataBlock:
    """
    EventDataBlock object

    - eid - the id for the event to be accessed in the REGISTERED_EVENTS dict
    - data - a dict containing event information
    """

    eid: int
    data: dict


class EventRegistry:
    def __init__(self, eid):
        """Event ID - only holds the eid - probably bad memory management lol"""
        self.eid = eid

# ------------ error ---------------- #
class RegistryNotFound(Exception):
    def __init__(self, eid):
        super().__init__(f"Event ID {eid} does not exist!")

