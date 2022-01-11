#for later "|"
import sys
import os

os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import glob

import tcod as libtcod
from entity import Entity
from input_handler import handle_keys
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_state import GameStates

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png") #Font/tileset

def main():
    screen_width = 80 #Screen size
    screen_height = 50
    map_width = 80 #Map size
    map_height = 45
    #Map generation parameters
    room_max_size = 10     
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3

    fov_algorithm = 2 #FOV-algorithm used - http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds
    fov_light_walls = True #Is FOV used to affect the visibility of things
    fov_radius = 10 

    #Some colors for current and later use
    colors = {
       'dark_wall': libtcod.Color(50, 50, 50),
       'dark_ground': libtcod.Color(50, 50, 50),
       'light_wall': libtcod.Color(255, 255, 255),
       'light_ground': libtcod.Color(100, 100, 100)
   }

    fov_recompute = True #Do not recompute fov every frame. Just when changes happen.
    player = Entity(int(screen_width / 2), int(screen_height/2), '@', libtcod.red, "Player", blocks=True) #Initializing the player
    entities = [player] #List of all the entities
    game_map = GameMap(map_width, map_height) #Initialize the game map
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room) #Generate the map

    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    libtcod.console_init_root(screen_width, screen_height, "libtcode game", False) # Configuring the game window/console
    con = libtcod.console_new(screen_width, screen_height) #Initializing the game window/console

    key = libtcod.Key() #See if a key is pressed
    mouse = libtcod.Mouse() #See if mouse is used

    fov_map = initialize_fov(game_map) #Initial state of the fov
    game_state = GameStates.PLAYERS_TURN #Gives the initiative to the player

    while not libtcod.console_is_window_closed(): #Main loop
        if fov_recompute: #Recomputes fov if needed
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse) #Check for keypresses

        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)
        libtcod.console_flush() #Updates to a newer version of the console, where blit has been drawing the new stuff

        clear_all(con, entities)
        
        #Movement handling (using the input_handler.py file)
        action = handle_keys(key)           

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        
        #Player turn logic
        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                destination_x = player.x + dx
                destination_y = player.y + dy
                target = Entity.get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    print("You kick the {} in the shins, much to its annoyance!".format(target.name))
                else:
                    fov_recompute = True
                    player.move(dx, dy)

            game_state = GameStates.ENEMY_TURN

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if exit:
            return True

        #Enemy turn logic
        if game_state == GameStates.ENEMY_TURN: 
            for entity in entities:
                if entity != player and fov_map.fov[entity.y][entity.x]:
                    print("The {} ponders the meaning of it's existence.".format(entity.name))
            
            game_state = GameStates.PLAYERS_TURN


if __name__ == "__main__":
    main()