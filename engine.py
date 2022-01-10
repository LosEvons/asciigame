#for later "|"
import sys
import os

from input_handler import handle_keys
os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import glob

from input_handler import handle_keys
import tcod as libtcod

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png") #Font/tileset

def main():
    screen_width = 80 #Screen size
    screen_height = 50

    player_x = int(screen_width/2) #Player starting cordinates.
    player_y = int(screen_height/2)

    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    libtcod.console_init_root(screen_width, screen_height, "libtcode game", False) # Configuring the game window/console
    con = libtcod.console_new(screen_width, screen_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed(): #Main loop
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse) #Check for keypresses
        libtcod.console_set_default_foreground(0, libtcod.white) #Sets the font default color
        libtcod.console_put_char(con, player_x, player_y, '@', libtcod.BKGND_NONE) #Positions the player
        libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0) #This actually draws the console
        libtcod.console_flush() #Update textures/draws them in the console

        libtcod.console_put_char(con, player_x, player_y, ' ', libtcod.BKGND_NONE)
        
        #Movement handling (using the input_handler.py file)
        action = handle_keys(key)           

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")

        if move:
            dx, dy = move
            player_x += dx
            player_y += dy

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if exit:
            return True

if __name__ == "__main__":
    main()