import tcod as libtcod
import os
import sys
os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import json

from entity import Entity
from components.fighter import Fighter
from components.item import Item
from components.equipment import Equipment
from game_messages import MessageLog
from game_state import GameStates
from components.inventory import Inventory
from components.level import Level
from components.equippable import Equippable
from equipment_slots import EquipmentSlots
from map_objects.game_map import GameMap
from render_functions import RenderOrder
from components.character_sheet import CharacterSheet

def get_game_variables(constants):
    fighter_component = Fighter(character_sheet=CharacterSheet(15, 15, 15, 12, 12, 12))
    inventory_component = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()
    
    player = Entity(0, 0, "@", libtcod.red, "Player", blocks=True, render_order=RenderOrder.ACTOR, 
        fighter=fighter_component, inventory=inventory_component, level=level_component,
        equipment=equipment_component, followers=[]) #Initializing the player
    cursor = Entity(50, 50, 'X', libtcod.light_red, "Cursor", render_order=RenderOrder.INVISIBLE)
    entities = [player, cursor] #List of all the entities
    
    equipment_component = Equippable(EquipmentSlots.MAIN_HAND, damage_dice=(2, 4), damage_bonus=1)
    dagger = Entity(0, 0, '-', libtcod.sky, "Dagger", equippable=equipment_component)

    equipment_component = Equippable(EquipmentSlots.WAIST, fuel=100)
    lantern = Entity(0, 0, '8', libtcod.light_orange, "Lantern", equippable=equipment_component)

    player.inventory.add_items(dagger)
    player.inventory.add_items(lantern)
    player.equipment.toggle_equip(dagger)
    player.equipment.toggle_equip(lantern)

    name_list = constants["name_list"]
    name_part_list = constants["name_part_list"]

    game_map = GameMap(constants["map_width"], constants["map_height"]) #Initialize the game map
    game_map.make_surface_map(constants["max_buildings"], constants["building_min_size"], constants["building_max_size"],
        constants["map_width"], constants["map_height"], constants["tree_max_size"], constants["tree_min_size"],
        constants["max_trees"], constants["min_trees"], player, entities, name_list, name_part_list, cursor)

    message_log = MessageLog(constants["message_x"], constants["message_width"], constants["message_height"])

    game_state = GameStates.PLAYERS_TURN #Gives the initiative to the player

    return player, entities, game_map, message_log, game_state, name_list, cursor, name_part_list

def get_constants():
    window_title = "Libtcod roguelike"

    screen_width = 128
    screen_height = 72

    sidebar_width = 10
    sidebar_height = screen_height

    bar_width = 22
    panel_height = 16
    panel_width = screen_width - sidebar_width
    panel_y = screen_height - panel_height
    panel_x = screen_width - panel_width

    utility_window_width = 30

    message_x = bar_width + 2
    message_width = panel_width - bar_width - 2
    message_height = panel_height - 2
    
    map_width = screen_width
    map_height = screen_height

    room_max_size = 12
    room_min_size = 4
    max_room = 35

    building_max_size = 12
    building_min_size = 6
    max_buildings = 10

    tree_max_size = 3
    tree_min_size = 1
    max_trees = 30
    min_trees = 20

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    name_list = get_name_list()
    name_part_list = get_name_part_list()

    special_char_list = get_special_characters()

    colors = {
       'dark_wall': libtcod.Color(50, 50, 50),
       'dark_ground': libtcod.Color(50, 50, 50),
       'light_wall': libtcod.Color(255, 255, 255),
       'light_ground': libtcod.Color(100, 100, 100)
       }

    key_color = [libtcod.dark_orange, libtcod.darkest_orange, libtcod.black]
    key_index = [0, int(fov_radius/2), fov_radius+1]
    lantern_color_map = libtcod.color_gen_map(key_color, key_index)

    key_color = [libtcod.green, libtcod.darker_green]
    key_index = [0, 200]
    grass_color_map = libtcod.color_gen_map(key_color, key_index)

    key_color=[libtcod.lightest_gray, libtcod.dark_grey, libtcod.dark_sepia]
    key_index = [0, 196, 200]
    stone_color_map = libtcod.color_gen_map(key_color, key_index)
    
    constants = {
        "window_title":window_title,                    #Game window title
        "screen_width":screen_width,                    #Size of screen
        "screen_height":screen_height,                  #
        "sidebar_width":sidebar_width,
        "sidebar_height":sidebar_height,
        "utility_window_width":utility_window_width,
        "bar_width":bar_width,                          #Health bar size
        "panel_height":panel_height,                    #Size of the UI panel (height and location)
        "panel_width":panel_width,
        "panel_y":panel_y,                              
        "panel_x":panel_x,
        "message_x":message_x,                          #Location of the message feed
        "message_width":message_width,                  #Size of the message feed
        "message_height":message_height,                #
        "map_width":map_width,                          #Size of game map
        "map_height":map_height,                        #
        "room_max_size":room_max_size,                  #Potential size of generated rooms
        "room_min_size":room_min_size,                  #
        "max_rooms":max_room,                           #Max rooms to be generated
        "tree_max_size":tree_max_size,
        "tree_min_size":tree_min_size,
        "max_trees":max_trees,
        "min_trees":min_trees,
        "fov_algorithm":fov_algorithm,                  #Determines the fov algorithm used
        "fov_light_walls":fov_light_walls,              #Determines if the fov lights walls
        "fov_radius":fov_radius,                        #Size of FOV
        "colors":colors,                                #A list of useful colors
        "name_list":name_list,                          #A list used for dynamic allocation of names to entities
        "special_char_list":special_char_list,
        "name_part_list":name_part_list,
        "building_max_size":building_max_size,
        "building_min_size":building_min_size,
        "max_buildings":max_buildings,
        "lantern_color_map":lantern_color_map,
        "grass_color_map":grass_color_map,
        "stone_color_map":stone_color_map
    }

    return constants

def get_name_list():
    DATA_FOLDER = "data"
    NAME_DATA_FILE = os.path.join(DATA_FOLDER, "name_data.json")
    with open(NAME_DATA_FILE, "r") as DATA_FILE:
        name_list = json.load(DATA_FILE)
        return name_list[0]

def get_name_part_list():
    DATA_FOLDER = "data"
    NAME_DATA_FILE = os.path.join(DATA_FOLDER, "name_data.json")
    with open(NAME_DATA_FILE, "r") as DATA_FILE:
        name_part_list = json.load(DATA_FILE)
        return name_part_list[1]

def get_special_characters():
    DATA_FOLDER = "data"
    CHAR_DATA = os.path.join(DATA_FOLDER, "special_characters_index.json")
    with open (CHAR_DATA, "r") as DATA_FILE:
        char_list = json.load(DATA_FILE)
        return char_list[0]