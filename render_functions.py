import tcod as libtcod
from enum import Enum

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)
    names = [entity.name for entity in entities
        if entity.x == x and entity.y == y and fov_map.fov[entity.y][entity.x]]
    names = ", ".join(names)

    return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width/2), y, libtcod.BKGND_NONE,
        libtcod.CENTER, "{}: {}/{}".format(name, value, maximum))

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
    screen_height, bar_width, panel_height, panel_y, mouse, colors):
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
        if fov_map.fov[entity.y][entity.x]: #If it's in our fov-range
            draw_entity(con, entity)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    render_bar(panel, 1, 1, bar_width, "HP", player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red)

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 
        get_names_under_mouse(mouse, entities, fov_map))

    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    """libtcod.console_set_default_foreground(con, libtcod.white)                          #Draws HP in the bottom left corner. Left here to be used as a template in the future
    libtcod.console_print_ex(con, 1, screen_height - 2, libtcod.BKGND_NONE, libtcod.LEFT, 
        "HP: {0:02}/{1:02}".format(player.fighter.hp, player.fighter.max_hp))"""

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0) #Blit draws stuff onto a hypothetical console. Flushing updates to the newer console.
    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)



def clear_all(con, entities): #Removes all entities one by one. Might become a source of performance issues. Otherwise we'd also see the previously drawn entities, and this would become an mspaint knockoff.
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity): 
    libtcod.console_set_default_foreground(con, entity.color) #Set the color of our entity
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE) #Set the character/texture for our character


def clear_entity(con, entity): #Takes an entity's position, and draws a white space in it's stead
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)