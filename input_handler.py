import tcod as libtcod

from game_state import GameStates

def handle_keys(key, game_state): #Determines which control-scheme to use
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY): #If this is in the form "== SHOW_INVENTORY or DROP_INVENTORY, it doesn't work for some reason. Don't know why, but sure thing buddy."
        return handle_inventory_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state == GameStates.LEVEL_UP: 
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)
    elif game_state == GameStates.LOOK:
        return handle_look_keys(key)

    return {}

def handle_character_screen(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {"exit":True}
    
    return {}


def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)
        
        if key_char == 'a':
            return {"level_up":"hp"}
        elif key_char == 'b':
            return {"level_up":"str"}
        elif key_char == 'c':
            return {"level_up":"def"}

    return {}

def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return{"new_game":True}
    elif key_char == 'b':
        return{"load_game":True}
    elif key_char == 'c':
        return{"exit":True}

    return {}

def handle_targeting_keys(key):
    key_char = chr(key.c)
    if key.vk == libtcod.KEY_ESCAPE:
        return {"targeting_canceled":True}

    if key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8:
        return {"cursor_move":(0,-1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2:
        return {"cursor_move":(0,1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4:
        return {"cursor_move":(-1,0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6:
        return {"cursor_move":(1,0)}
    elif key_char == 'y' or key.vk == libtcod.KEY_KP7:
        return {"cursor_move":(-1,-1)}
    elif key_char == 'u' or key.vk == libtcod.KEY_KP9:
        return {"cursor_move":(1,-1)}
    elif key_char == 'b' or key.vk == libtcod.KEY_KP1:
        return {"cursor_move":(-1,1)}
    elif key_char == 'n' or key.vk == libtcod.KEY_KP3:
        return {"cursor_move":(1,1)}
    
    elif key.vk == libtcod.KEY_ENTER:
        return {"chosen_target":True}
    
    return {}

def handle_look_keys(key):
    key_char = chr(key.c)
    if key.vk == libtcod.KEY_ESCAPE or key_char == 'q':
        return {"look_cancel":True}

    if key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8:
        return {"cursor_move":(0,-1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2:
        return {"cursor_move":(0,1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4:
        return {"cursor_move":(-1,0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6:
        return {"cursor_move":(1,0)}
    elif key_char == 'y' or key.vk == libtcod.KEY_KP7:
        return {"cursor_move":(-1,-1)}
    elif key_char == 'u' or key.vk == libtcod.KEY_KP9:
        return {"cursor_move":(1,-1)}
    elif key_char == 'b' or key.vk == libtcod.KEY_KP1:
        return {"cursor_move":(-1,1)}
    elif key_char == 'n' or key.vk == libtcod.KEY_KP3:
        return {"cursor_move":(1,1)}
    
    elif key.vk == libtcod.KEY_ENTER:
        return {"look_at":True}
    
    return {}

def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {"left_click":(x, y)}
    elif mouse.rbutton_pressed:
        return {"right_click":(x, y)}
    
    return {}

def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return{"inventory_index":index}
    
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        return{"fullscreen":True}
    elif key.vk == libtcod.KEY_ESCAPE:
        return{"exit":True}
    
    return {}


#Used as a place for all of our player controls
def handle_player_turn_keys(key):
    key_char = chr(key.c)
    #movement keys
    if key.vk == libtcod.KEY_UP or key_char == 'k' or key.vk == libtcod.KEY_KP8:
        return {"move":(0,-1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j' or key.vk == libtcod.KEY_KP2:
        return {"move":(0,1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h' or key.vk == libtcod.KEY_KP4:
        return {"move":(-1,0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l' or key.vk == libtcod.KEY_KP6:
        return {"move":(1,0)}
    elif key_char == 'y' or key.vk == libtcod.KEY_KP7:
        return {"move":(-1,-1)}
    elif key_char == 'u' or key.vk == libtcod.KEY_KP9:
        return {"move":(1,-1)}
    elif key_char == 'b' or key.vk == libtcod.KEY_KP1:
        return {"move":(-1,1)}
    elif key_char == 'n' or key.vk == libtcod.KEY_KP3:
        return {"move":(1,1)}

    if key_char == 'g':
        return{"pickup":True}

    if key_char == 'i':
        return {"show_inventory":True}

    if key_char == 'd':
        return{"drop_inventory":True}

    if key_char == 'c':
        return{"show_character_screen":True}

    if key_char == '<':
        return{"take_stairs":True}

    if key_char == 'q':
        return{"look":True}

    elif key_char == 'z':
        return {"wait":True}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        return {"fullscreen": True}

    elif key.vk == libtcod.KEY_ESCAPE:
        #Exit the game
        return {"exit": True}

    return {}