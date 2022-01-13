from components import ai
from components.ai import BasicMonster
from components.fighter import Fighter
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint
import tcod as libtcod
from entity import Entity
"""
This is used to generate the game map.
"""

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.unique_id = 0

    def initialize_tiles(self): #Creates a coordinate system of every tile. By default blocking and vision blocking is set to True.
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room):
        rooms = [] #Array of all the rooms and their properties. Appaerntly in the form: (anchor_x, anchor_y, size_x, size_y)
        num_rooms = 0
        for r in range (max_rooms): #Generate the max amount of rooms
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h) #We make a new room template.

            for other_room in rooms: #If our room intersects with another, we cancel the process and try again.
                if new_room.intersect(other_room):
                    break
            else:
                # did not break, means no intersections
                self.create_room(new_room) #We make the new room by changing blocked and block_sight to False

                (new_x, new_y) = new_room.center() #Now we find the center of our room.

                if num_rooms == 0: #If there are no other rooms, we make our player coordinates the center. Not sure why though...
                    player.x = new_x
                    player.y = new_y
                else:                                                   #Otherwise we take the coordinates of the previous room, 
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()    #we draw a tunnel between the rooms. Random decides wether 
                    if randint(0, 1) == 1:                              #Random decides whether we build the vertical or horizontal bit 1.    
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, max_monsters_per_room) #Here we generate entities for each room
                rooms.append(new_room) #Finally we add the room to our index and mark it in the room counter
                num_rooms += 1


    def create_room(self, room): #Changes the tile type in a x*y space. 
        for x in range (room.x1 + 1, room.x2):
            for y in range (room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y): #Changes the tile type in a x1*x2+1 space. This is used to make small restricted hallways.
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
    
    def create_v_tunnel(self, y1, y2, x): #Same as with the previous tunnel algo
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y): #Checks if the tile we are currently looking at has blocking set to True
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, room, entities, max_monsters_per_room): #Randomly decides a place in the room for our monsters
        number_of_monsters = randint(0, max_monsters_per_room) #Set the number of monsters for the current room
        ai_component = BasicMonster()
        for i in range(number_of_monsters): #Iterate through all the monsters
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any ([entity for entity in entities if entity.x == x and entity.y == y]): #Let's not stack multiple entities on the same tile
                if randint(0, 100) < 80: #We randomize between two different monsters
                    fighter_component = Fighter(hp=10, defense=0, power=3)
                    monster = Entity(x, y, 'o', libtcod.desaturated_green, "Goblin" + str(self.unique_id), blocks=True, fighter=fighter_component, ai=ai_component)
                else:
                    fighter_component = Fighter(hp=16, defense=1, power=4)
                    monster = Entity(x, y, 'T', libtcod.darker_green, "Hydra" + str(self.unique_id), blocks=True, fighter=fighter_component, ai=ai_component)

                entities.append(monster) #Add the monster to our list of entities
                self.unique_id += 1 #Give every monster a unique id. Might come in clutch later.
                    