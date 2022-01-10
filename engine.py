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


DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png") #Font/tileset

def main():
    screen_width = 80 #Screen size
    screen_height = 50
    map_width = 80
    map_height = 45
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    colors = {
       'dark_wall': libtcod.Color(200, 200, 200),
       'dark_ground': libtcod.Color(55, 55, 55)
   }

    player = Entity(int(screen_width / 2), int(screen_height/2), '@', libtcod.white)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), 'g', libtcod.yellow)
    entities = [npc, player]
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    libtcod.console_init_root(screen_width, screen_height, "libtcode game", False) # Configuring the game window/console
    con = libtcod.console_new(screen_width, screen_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed(): #Main loop
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse) #Check for keypresses

        render_all(con, entities, game_map, screen_width, screen_height, colors)
        libtcod.console_flush() #Update textures/draws them in the console

        clear_all(con, entities)
        
        #Movement handling (using the input_handler.py file)
        action = handle_keys(key)           

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if exit:
            return True

if __name__ == "__main__":
    main()