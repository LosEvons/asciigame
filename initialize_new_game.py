import tcod as libtcod

from entity import Entity
from components.fighter import Fighter
from game_messages import MessageLog
from game_state import GameStates
from components.inventory import Inventory
from components.level import Level
from map_objects.game_map import GameMap
from render_functions import RenderOrder

def get_game_variables(constants):
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    level_component = Level()

    player = Entity(0, 0, '@', libtcod.red, "Player", blocks=True, render_order=RenderOrder.ACTOR, 
        fighter=fighter_component, inventory=inventory_component, level=level_component) #Initializing the player
    entities = [player] #List of all the entities

    game_map = GameMap(constants["map_width"], constants["map_height"]) #Initialize the game map
    game_map.make_map(constants["max_rooms"], constants["room_min_size"], constants["room_max_size"], 
        constants["map_width"], constants["map_height"], player, entities) #Generate the map

    message_log = MessageLog(constants["message_x"], constants["message_width"], constants["message_height"])

    game_state = GameStates.PLAYERS_TURN #Gives the initiative to the player

    return player, entities, game_map, message_log, game_state

def get_constants():
    window_title = "Libtcod roguelike"

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1
    
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_room = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
       'dark_wall': libtcod.Color(50, 50, 50),
       'dark_ground': libtcod.Color(50, 50, 50),
       'light_wall': libtcod.Color(255, 255, 255),
       'light_ground': libtcod.Color(100, 100, 100)
       }
    
    constants = {
        "window_title":window_title,                    #Game window title
        "screen_width":screen_width,                    #Size of screen
        "screen_height":screen_height,                  #
        "bar_width":bar_width,                          #Health bar size
        "panel_height":panel_height,                    #Size of the UI panel (height and location)
        "panel_y":panel_y,                              #
        "message_x":message_x,                          #Location of the message feed
        "message_width":message_width,                  #Size of the message feed
        "message_height":message_height,                #
        "map_width":map_width,                          #Size of game map
        "map_height":map_height,                        #
        "room_max_size":room_max_size,                  #Potential size of generated rooms
        "room_min_size":room_min_size,                  #
        "max_rooms":max_room,                            #Max rooms to be generated
        "fov_algorithm":fov_algorithm,                  #Determines the fov algorithm used
        "fov_light_walls":fov_light_walls,              #Determines if the fov lights walls
        "fov_radius":fov_radius,                        #Size of FOV
        "colors":colors                                 #A list of useful colors
    }

    return constants