import tcod as libtcod
from enum import Enum
from game_state import GameStates
from menus import character_screen, inventory_menu, level_up_menu

class RenderOrder(Enum):
    STAIRS = 1
    ITEM = 2
    CORPSE = 3
    ACTOR = 4


def get_names_under_mouse(mouse, entities, fov_map): #Displays the name of stuff under our mouse on the UI.
    (x, y) = (mouse.cx, mouse.cy) #Get mouse pos
    names = [entity.name for entity in entities
        if entity.x == x and entity.y == y and fov_map.fov[entity.y][entity.x]] #List of entity names if entities are visible and under our mouse
    names = ", ".join(names)

    return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color): #Render the HP bar
    bar_width = int(float(value) / maximum * total_width) #Define how long the hp bar should be

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN) #Draws the back of our bar
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN) #Draws the front of our bar, which changes size depending on 
                                                                                     #on the amount of player hp
    libtcod.console_set_default_foreground(panel, libtcod.white) 
    libtcod.console_print_ex(panel, int(x + total_width/2), y, libtcod.BKGND_NONE, #Defines the hp indication text
        libtcod.CENTER, "{}: {}/{}".format(name, value, maximum))

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
    screen_height, bar_width, panel_height, panel_y, mouse, colors, game_state):
    if fov_recompute:
        for y in range(game_map.height):        # Draw all the tiles in the game map
            for x in range(game_map.width):
                visible = fov_map.fov[y][x]     #Makes an array of all the stuff inside our FOV
                wall = game_map.tiles[x][y].block_sight and game_map.tiles[x][y].blocked #defines a wall
                if visible:             #If it's visible (in the fov), draw it
                    if wall:
                        libtcod.console_set_default_foreground(con, colors.get('light_wall'))
                        libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                    else:
                        libtcod.console_set_default_foreground(con, colors.get('light_ground'))
                        libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored: # If it has been seen previously, draw it but darker.
                
                    if wall:
                        #libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET) <-- Solid background
                        libtcod.console_set_default_foreground(con, colors.get('dark_wall'))
                        libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                    else:
                        #libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET) <-- Solid background
                        libtcod.console_set_default_foreground(con, colors.get('dark_ground'))
                        libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    
    for entity in entities_in_render_order:         # Draw all entities in the list
        if fov_map.fov[entity.y][entity.x] or (entity.stairs and game_map.tiles[entity.x][entity.y].explored): #If it's in our fov-range
            draw_entity(con, entity)

    libtcod.console_set_default_background(panel, libtcod.black)#Sets the UI background as black
    libtcod.console_clear(panel) #Clears UI before drawing it again

    render_bar(panel, 1, 1, bar_width, "HP", player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red) #Draws the hp bar

    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, "Dungeon level: {}".format(game_map.dungeon_level))

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,  #Draws stuff in the ui when enemy is moused over
        get_names_under_mouse(mouse, entities, fov_map))

    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color) #Draws messages in the UI, and y makes sure older messages get removed and messages stack
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    """libtcod.console_set_default_foreground(con, libtcod.white)                          #Draws HP in the bottom left corner. Left here to be used as a template in the future
    libtcod.console_print_ex(con, 1, screen_height - 2, libtcod.BKGND_NONE, libtcod.LEFT, 
        "HP: {0:02}/{1:02}".format(player.fighter.hp, player.fighter.max_hp))"""

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0) #Blit draws stuff onto a hypothetical console. Flushing updates to the newer console.
    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y) #Draws our UI element into the console

    inventory_title = None
    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = "Press the key next to an item to use it, or Esc to cancel.\n"
        elif game_state == GameStates.DROP_INVENTORY:
            inventory_title = "Press the key next to an item to drop it, or Esc to cancel.\n"

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    if game_state == GameStates.LEVEL_UP:
        level_up_menu(con, "Level up! Choose a stat to raise:", player, 40, 
            screen_width, screen_height)

    if game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)



def clear_all(con, entities): #Removes all entities one by one. Might become a source of performance issues. Otherwise we'd also see the previously drawn entities, and this would become an mspaint knockoff.
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity): 
    libtcod.console_set_default_foreground(con, entity.color) #Set the color of our entity
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE) #Set the character/texture for our character


def clear_entity(con, entity): #Takes an entity's position, and draws a white space in it's stead
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)