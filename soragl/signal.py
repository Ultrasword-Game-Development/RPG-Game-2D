
from queue import deque, Queue



# ------------------------------------------------------------ #
# static handler
# ------------------------------------------------------------ #

SIGNALS = {}
EMIT_QUEUE = Queue(100)

def register_signal(signal_register: "SignalRegister"):
    """Register a signal to the system"""
    SIGNALS[signal_register.id] = signal_register

def handle_signals():
    """Handle all emitted signals"""
    while not EMIT_QUEUE.empty():
        # get and update
        s, args = EMIT_QUEUE.get()
        s._emit_signal(*args)

# ------------------------------------------------------------ #
# signal receivers
# ------------------------------------------------------------ #

class Receiver:
    """
    Receiver:
    - id: int
    - _call: function
    - active: boolean

    when created, allows the user to essentially remove or add a receiver
    object to a signal
    - thus signals can essentially be activated and deactivated
    """
    def __init__(self, function):
        """Initialize a receiveer object"""
        self.id = id(self)
        self._call = function
        self.active = True
    
    def call(self, args: tuple):
        """Call a receiver"""
        if not self.active: return
        self._call(*args)


# ------------------------------------------------------------ #
# signals
# ------------------------------------------------------------ #

class SignalRegister:
    """
    Signal
    - name: str
    - receivers: dict

    an object that is instantiated to hold data about different types of signals
    """
    def __init__(self, name: str):
        """Create a signal object"""
        self.id = id(self)
        self.name = name
        self.receivers = {}
    
    def add_receiver(self, receiver: Receiver):
        """Add receivers to this signal - receivers are functions"""
        self.receivers[receiver.id] = receiver
        return receiver
    
    def remove_receiver(self, receiver: "Receiver or int"):
        """Remove receivers to a signal"""
        if type(receiver) == int:
            return self.receivers.pop(receiver)
        return self.receivers.pop(receiver.id)
    
    def emit_signal(self, *args):
        """Queue a signal to be emitted -- the one to actually call"""
        EMIT_QUEUE.put((self, args))

    def _emit_signal(self, *args):
        """Call all receiver functions"""
        for rec in self.receivers:
            self.receivers[rec].call(args)
        
    def __repr__(self):
        """Represent the signal as a string"""
        return f"signal: {self.name} | id: {self.id}"






