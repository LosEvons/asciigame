from components.equipment import Equipment
from components.equippable import Equippable
from components.ai import BasicMonster
from components.fighter import Fighter
from equipment_slots import EquipmentSlots
from game_messages import Message
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint
import tcod as libtcod
from entity import Entity
from render_functions import RenderOrder
from components.item import Item
from item_functions import cast_confusion, cast_fireball, cast_lightning, heal
from components.stairs import Stairs
from random_utils import from_dungeon_level, random_choice_from_dict
"""
This is used to generate the game map.
"""

class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.unique_id = 0
        self.dungeon_level = dungeon_level

    def initialize_tiles(self): #Creates a coordinate system of every tile. By default blocking and vision blocking is set to True.
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, 
        player, entities):
        rooms = [] #Array of all the rooms and their properties. Appaerntly in the form: (anchor_x, anchor_y, size_x, size_y)
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

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

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

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

                self.place_entities(new_room, entities) #Here we generate entities for each room
                rooms.append(new_room) #Finally we add the room to our index and mark it in the room counter
                num_rooms += 1
        stairs_component = Stairs(self.dungeon_level +1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, 
            '>', libtcod.white, "Stairs", render_order=RenderOrder.STAIRS, 
            stairs=stairs_component)
        entities.append(down_stairs)

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants["max_rooms"], constants["room_min_size"], constants["room_max_size"],
            constants["map_width"], constants["map_height"], player, entities)
        
        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message("You take a moment to rest, and recover your strenght.", libtcod.light_violet))

        return entities


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

    def place_entities(self, room, entities): #Randomly decides a place in the room for our monsters
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        number_of_monsters = randint(0, max_monsters_per_room) #Set the number of monsters for the current room
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            "goblin":80, 
            "hydra":from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
            }

        item_chances = {
            "healing_potion":70, 
            "lightning_scroll":from_dungeon_level([[25, 4]], self.dungeon_level), 
            "fireball_scroll":from_dungeon_level([[25, 6]], self.dungeon_level), 
            "confusion_scroll":from_dungeon_level([[25, 2]], self.dungeon_level),
            "sword":from_dungeon_level([[5, 4]], self.dungeon_level),
            "shield":from_dungeon_level([[15, 0]], self.dungeon_level)
            }

        for i in range(number_of_monsters): #Iterate through all the monsters
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any ([entity for entity in entities if entity.x == x and entity.y == y]): #Let's not stack multiple entities on the same tile
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == "goblin": #We randomize between two different monsters
                    ai_component = BasicMonster()
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    monster = Entity(x, y, 'o', libtcod.desaturated_green, "Goblin" + str(self.unique_id), blocks=True, 
                        render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                elif monster_choice == "hydra":
                    ai_component = BasicMonster()
                    fighter_component = Fighter(hp=30, defense=1, power=9, xp=100)
                    monster = Entity(x, y, 'T', libtcod.darker_green, "Hydra" + str(self.unique_id), blocks=True, 
                        render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

                entities.append(monster) #Add the monster to our list of entities
                self.unique_id += 1 #Give every monster a unique id. Might come in clutch later.
                    
        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room .y2 - 1)
            item_component = Item(use_function=heal, amount=4)

            if not any ([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)
                if item_choice == "healing_potion":
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(x, y, '!', libtcod.violet, "Healing Potion", render_order=RenderOrder.ITEM,
                        item=item_component)
                elif item_choice == "fireball_scroll":
                    item_component = Item(use_function=cast_fireball, targeting=True,
                        targeting_message=Message("Left-click a taret tile for the fireball, or right click to cancel.", libtcod.white),
                        damage=12, radius=3)
                    item = Entity(x, y, '?', libtcod.red, "Fireball Scroll", render_order=RenderOrder.ITEM,
                        item=item_component)
                elif item_choice == "confusion_scroll":
                    item_component = Item(use_function=cast_confusion, targeting=True,
                        targeting_message=Message("Left-click an enemy to confuse it, or right-click to cancel.", libtcod.white))
                    item = Entity(x, y, '?', libtcod.light_pink, "Confusion Scroll", render_order=RenderOrder.ITEM,
                        item=item_component)
                elif item_choice == "lightning_scroll":
                    item_component = Item(use_function=cast_lightning, damage=20, maximum_range=5)
                    item = Entity(x, y, '?', libtcod.yellow, "Lightning Scroll", render_order=RenderOrder.ITEM,
                        item=item_component)
                elif item_choice == "sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
                    item = Entity(x, y, "/", libtcod.sky, "Sword", render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                elif item_choice == "shield":
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x, y, "[", libtcod.darker_orange, "Shield", render_order=RenderOrder.ITEM,
                        equippable=equippable_component)

                entities.append(item)