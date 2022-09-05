import engine
from engine.network import server

from engine import scenehandler


def add_entity(s, h, e):
    h.add_entity(e)
    s.send_to_all({"type": "CreateEntity", "data": e})


def main(server):
    __scene = scenehandler.Scene()
    __handler = __scene.handler
    # ----------------------------------- #
    # create world
    m = mage.Mage()
    m.position.xy = (100, 100)

    p = peasant.Peasant()
    p.position.xy = (200, 200)
    p2 = peasant.Peasant()
    p2.position.xy = (100, 100)

    # ----------------------------------- #
    __handler.add_entity(m)
    __handler.add_entity(p)
    __handler.add_entity(p2)

SERVER = server.Server()
SERVER.run()
SERVER.close()


