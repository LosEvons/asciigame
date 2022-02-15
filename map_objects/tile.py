class Tile:
    """
    A tile on a map. Can block movement and sight
    """
    def __init__(self, blocked, block_sight=None, door=None, grass=None, floor=None, wall=False, vwall=False, hwall=False, 
        tlwall=None, trwall=None, brwall=None, blwall=None, debug=None, debug2=None):
        self.blocked = blocked
        self.debug = debug
        self.debug2 = debug2

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight #By default tiles block sight
        self.explored = False #Check if a tile has been seen before

        self.door = door
        self.grass = grass
        self.floor = floor

        self.wall = wall
        self.vwall = vwall
        self.hwall = hwall
        self.trwall = trwall
        self.tlwall = tlwall
        self.brwall = brwall
        self.blwall = blwall