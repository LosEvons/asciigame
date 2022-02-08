from components.character_sheet import CharacterSheet
from components.equipment import Equipment
from components.equippable import Equippable
from components.ai import BasicMonster
from components.fighter import Fighter
from equipment_slots import EquipmentSlots
from game_messages import Message
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint, choice
import tcod as libtcod
from entity import Entity
from render_functions import RenderOrder
from components.item import Item
from item_functions import cast_confusion, cast_fireball, cast_lightning, heal
from components.stairs import Stairs
from random_utils import from_dungeon_level, random_choice_from_dict
from components.name import Name, name_from_parts
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

    def get_adjacent_tiles(self, x, y):
        adjacent_tiles = {
            "up":self.tiles[x][y-1],
            "down":self.tiles[x][y+1],
            "left":self.tiles[x-1][y],
            "right":self.tiles[x+1][y]
        }
        return adjacent_tiles
    
    def make_surface_map(self, max_buildings, building_min_size, building_max_size, map_width, map_height,
        player, entities, name_list, name_part_list, cursor):
        buildings = []
        num_buildings = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for x in range(map_width-2):
            for y in range(map_height-2):
                self.tiles[x+1][y+1].blocked = False
                self.tiles[x+1][y+1].block_sight = False

        for b in range(max_buildings):
            w = randint(building_min_size, building_max_size)
            h = randint(building_min_size, building_max_size)
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_building = Rect(x, y, w, h)

            for other_building in buildings:
                if new_building.intersect(other_building):
                    break
            else:
                self.create_building(new_building)
                (new_x, new_y) = new_building.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_buildings == 0:
                    player.x = new_x
                    player.y = new_y

                self.place_entities(new_building, entities, name_list, name_part_list)
                buildings.append(new_building)
                num_buildings += 1
        
        #Attempt at fixing rooms not having doors
        shared_tiles = []
        for building in buildings:
            for othr_bldn in buildings:
                if building != othr_bldn and building.intersect(othr_bldn):
                    shared_tiles.append(building.get_shared_tiles(othr_bldn))
        
        print(shared_tiles)
            
        stairs_component = Stairs(self.dungeon_level +1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, 
            '>', libtcod.white, "Stairs", render_order=RenderOrder.STAIRS, 
            stairs=stairs_component)
        entities.append(down_stairs)


    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, 
        player, entities, name_list, name_part_list, cursor):
        rooms = [] #Array of all the rooms and their properties. Appaerntly in the form: (anchor_x, anchor_y, size_x, size_y)
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range (max_rooms): #Generate the max amount of rooms
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w)
            y = randint(0, map_height - h )

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

                self.place_entities(new_room, entities, name_list, name_part_list) #Here we generate entities for each room
                rooms.append(new_room) #Finally we add the room to our index and mark it in the room counter
                num_rooms += 1
        stairs_component = Stairs(self.dungeon_level +1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, 
            '>', libtcod.white, "Stairs", render_order=RenderOrder.STAIRS, 
            stairs=stairs_component)
        entities.append(down_stairs)

    def next_floor(self, player, message_log, constants, name_list, name_part_list, cursor):
        self.dungeon_level += 1
        entities = [player, cursor]

        self.tiles = self.initialize_tiles()
        self.make_map(constants["max_rooms"], constants["room_min_size"], constants["room_max_size"],
            constants["map_width"], constants["map_height"], player, entities, name_list, name_part_list, cursor)
        
        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message("You take a moment to rest, and recover your strenght.", libtcod.light_violet))

        return entities


    def create_room(self, room): #Changes the tile type in a x*y space. 
        for x in range (room.x1 + 1, room.x2):
            for y in range (room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
    
    def create_building(self, building):
        for x in range(building.x1, building.x2 + 1):
            self.tiles[x][building.y1].blocked = True
            self.tiles[x][building.y1].block_sight = True
            self.tiles[x][building.y2].blocked = True
            self.tiles[x][building.y2].block_sight = True
        for y in range(building.y1, building.y2 + 1):
            self.tiles[building.x1][y].blocked = True
            self.tiles[building.x1][y].block_sight = True
            self.tiles[building.x2][y].blocked = True
            self.tiles[building.x2][y].block_sight = True

        for x in range(building.x1 + 2, building.x2 - 1):
            for y in range(building.y1 + 2, building.y2 - 1):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

        while True:
            door = choice(choice(building.edge))
            if door not in (building.tl_corner, building.tr_corner, building.bl_corner, building.br_corner):
                self.tiles[door[0]][door[1]].blocked = False
                self.tiles[door[0]][door[1]].block_sight = False
                break

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

    def place_entities(self, room, entities, name_list, name_part_list): #Randomly decides a place in the room for our monsters
        max_monsters_per_room = from_dungeon_level([[1, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[2, 1], [2, 4]], self.dungeon_level)
        number_of_monsters = randint(0, max_monsters_per_room) #Set the number of monsters for the current room
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            "hound":from_dungeon_level([[80, 1], [50, 2], [10, 3], [0, 4]], self.dungeon_level),
            "goblin":from_dungeon_level([[50, 2], [80, 3]], self.dungeon_level), 
            "hydra":from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
            }

        item_chances = {
            "healing_potion":30, 
            "lightning_scroll":from_dungeon_level([[25, 4]], self.dungeon_level), 
            "fireball_scroll":from_dungeon_level([[25, 1]], self.dungeon_level), 
            "confusion_scroll":from_dungeon_level([[25, 1]], self.dungeon_level),
            "shield":from_dungeon_level([[60, 1], [10, 2], [0, 3]], self.dungeon_level),
            "1d6sword":from_dungeon_level([[40, 1], [10, 2], [0, 3]], self.dungeon_level),
            "1d8sword":from_dungeon_level([[30, 2], [10, 3], [5 ,4], [0, 5]], self.dungeon_level),
            "2d6sword":from_dungeon_level([[20, 4]], self.dungeon_level),
            "2d8sword":from_dungeon_level([[10, 6]],self.dungeon_level),
            "helmet":from_dungeon_level([[60, 1], [10, 2], [0, 3]], self.dungeon_level),
            "shoulderpads":from_dungeon_level([[15, 4], [10, 5], [0, 7]], self.dungeon_level),
            "chestplate":from_dungeon_level([[5, 5], [15, 6], [0, 8]], self.dungeon_level),
            "armguards":from_dungeon_level([[15, 3], [5, 4], [0, 6]], self.dungeon_level),
            "belt":from_dungeon_level([[10, 1], [20, 3], [0, 5]], self.dungeon_level),
            "bracers":from_dungeon_level([[10, 1], [25, 3], [0, 4]], self.dungeon_level),
            "boots":from_dungeon_level([[10, 2], [15, 3], [10, 3], [0, 5]], self.dungeon_level)
            }

        for i in range(number_of_monsters): #Iterate through all the monsters
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any ([entity for entity in entities if entity.x == x and entity.y == y]): #Let's not stack multiple entities on the same tile
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == "hound":
                    ai_component = BasicMonster()
                    fighter_component = Fighter(character_sheet=CharacterSheet(6, 6, 6, 6, 6, 6), xp = 30)
                    monster = Entity(x, y, 'h', libtcod.dark_orange, name_from_parts(name_part_list), blocks=True,
                        render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                elif monster_choice == "goblin": #We randomize between two different monsters
                    ai_component = BasicMonster()
                    fighter_component = Fighter(character_sheet=CharacterSheet(8, 8, 8, 8, 8, 8), xp=50)
                    monster = Entity(x, y, 'g', libtcod.desaturated_green, name_from_parts(name_part_list), blocks=True, 
                        render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                elif monster_choice == "hydra":
                    ai_component = BasicMonster()
                    fighter_component = Fighter(character_sheet=CharacterSheet(10, 10, 10, 10, 10, 10), xp=100)
                    monster = Entity(x, y, 'H', libtcod.darker_green, Name(name_list, "hydra"), blocks=True, 
                        render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

                entities.append(monster) #Add the monster to our list of entities
                self.unique_id += 1 #Give every monster a unique id. Might come in clutch later.
                    
        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room .y2 - 1)

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
                
                elif item_choice == "1d6sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, damage_dice=(1,6), damage_bonus=randint(0, 5))
                    item = Entity(x, y, "/", libtcod.sky, Name(name_list, "sword"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                elif item_choice == "1d8sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, damage_dice=(1,8), damage_bonus=randint(0, 5))
                    item = Entity(x, y, "/", libtcod.sky, Name(name_list, "sword"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                elif item_choice == "2d6sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, damage_dice=(2,6), damage_bonus=randint(0, 10))
                    item = Entity(x, y, "/", libtcod.sky, Name(name_list, "sword"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                elif item_choice == "2d8sword":
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, damage_dice=(2,8), damage_bonus=randint(0, 10))
                    item = Entity(x, y, "/", libtcod.sky, Name(name_list, "sword"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
            
                elif item_choice == "shield":
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, ac_bonus=2, max_hp_bonus=1)
                    item = Entity(x, y, "[", libtcod.darker_orange, Name(name_list, "shield"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)

                elif item_choice == "helmet":
                    equippable_component = Equippable(EquipmentSlots.HEAD, ac_bonus=1, max_hp_bonus=2)
                    item = Entity(x, y, "^", libtcod.dark_orange, Name(name_list, "helmet"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)

                elif item_choice == "chestplate":
                    equippable_component = Equippable(EquipmentSlots.CHEST, ac_bonus=0, max_hp_bonus=randint(0, 20))
                    item = Entity(x, y, "c", libtcod.dark_orange, Name(name_list, "chestplate"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                
                elif item_choice == "shoulderpads":
                    equippable_component = Equippable(EquipmentSlots.SHOULDERS, ac_bonus=1, max_hp_bonus=0)
                    item = Entity(x, y, "s", libtcod.dark_orange, Name(name_list, "shoulderpads"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                
                elif item_choice == "armguards":
                    equippable_component = Equippable(EquipmentSlots.ARMS, ac_bonus=1, max_hp_bonus=2)
                    item = Entity(x, y, "a", libtcod.dark_orange, Name(name_list, "armguards"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                
                elif item_choice == "belt":
                    equippable_component = Equippable(EquipmentSlots.WAIST, ac_bonus=1, max_hp_bonus=3)
                    item = Entity(x, y, "B", libtcod.dark_orange, Name(name_list, "belt"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                
                elif item_choice == "bracers":
                    equippable_component = Equippable(EquipmentSlots.LEGS, ac_bonus=0, max_hp_bonus=randint(0, 15))
                    item = Entity(x, y, "p", libtcod.dark_orange, Name(name_list, "bracers"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                
                elif item_choice == "boots":
                    equippable_component = Equippable(EquipmentSlots.FEET, ac_bonus=1, max_hp_bonus=2)
                    item = Entity(x, y, "b", libtcod.dark_orange, Name(name_list, "boots"), render_order=RenderOrder.ITEM,
                        equippable=equippable_component)
                

                entities.append(item)