from engine.network import network_obj as neto
from engine import scenehandler

# ----------------------------------- #
# scene entity updates
class EntityUpdates:
    NAME = "EntityUpdates"
    def handle(data: dict):
        return

    def pack(entity):
        # updates positions of all entities
        return entity


class CreateEntity:
    NAME = "CreateEntity"
    def handle(data: dict):
        return
    
    def pack(data):
        return {}

