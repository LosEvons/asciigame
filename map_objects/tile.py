import tcod as libtcod
from map_objects.tilestyle import TileStyle

class Tile:
    """
    A tile on a map. Can block movement and sight
    """
    def __init__(self, blocked, block_sight=None, door=None, grass=None, floor=None, wall=False, vwall=False, hwall=False, 
        tlwall=None, trwall=None, brwall=None, blwall=None, debug=None, debug2=None, tree=None, shade=None, style=None):
        self.blocked = blocked
        self.debug = debug
        self.debug2 = debug2
        self.style = style

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight #By default tiles block sight
        self.explored = False #Check if a tile has been seen before

        self.door = door
        self.grass = grass
        self.floor = floor
        self.tree = tree
        self.shade = shade

        self.wall = wall
        self.vwall = vwall
        self.hwall = hwall
        self.trwall = trwall
        self.tlwall = tlwall
        self.brwall = brwall
        self.blwall = blwall

    @property
    def tilestyle(self):
        tilestyle = {}
        if self.style == TileStyle.WALL:
            tilestyle["char"] = "0"
            tilestyle["charcol"] = libtcod.Color(255, 255, 255)
            tilestyle["backcol"] = libtcod.darkest_grey
        elif self.style == TileStyle.GRASS:
            tilestyle["char"] = "0"
            tilestyle["charcol"] = libtcod.Color(255, 255, 255)
            tilestyle["backcol"] = libtcod.darkest_grey
        elif self.style == TileStyle.DOOR:
            tilestyle["char"] = "0"
            tilestyle["charcol"] = libtcod.Color(255, 255, 255)
            tilestyle["backcol"] = libtcod.darkest_grey
        elif self.style == TileStyle.FLOOR:
            tilestyle["char"] = "0"
            tilestyle["charcol"] = libtcod.Color(255, 255, 255)
            tilestyle["backcol"] = libtcod.darkest_grey
        elif self.style == TileStyle.WOOD:
            tilestyle["char"] = "0"
            tilestyle["charcol"] = libtcod.Color(255, 255, 255)
            tilestyle["backcol"] = libtcod.darkest_grey
        
        return tilestyle