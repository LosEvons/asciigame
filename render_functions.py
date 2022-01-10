import tcod as libtcod
from tcod import color


def render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors):
    for y in range(game_map.height):        # Draw all the tiles in the game map
        for x in range(game_map.width):
            visible = fov_map.fov[y][x]     #Makes an array of all the stuff inside our FOV
            wall = game_map.tiles[x][y].block_sight
            if visible:             #Computes FOV
                if wall:
                    libtcod.console_set_default_foreground(con, colors.get('light_wall'))
                    libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                else:
                    libtcod.console_set_default_foreground(con, colors.get('light_ground'))
                    libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
                game_map.tiles[x][y].explored = True
            elif game_map.tiles[x][y].explored:
                if wall:
                    #libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET) <-- Solid background
                    libtcod.console_set_default_foreground(con, colors.get('dark_wall'))
                    libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                else:
                    #libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET) <-- Solid background
                    libtcod.console_set_default_foreground(con, colors.get('dark_ground'))
                    libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
            
    
    
    for entity in entities:         # Draw all entities in the list
        if fov_map.fov[entity.y][entity.x]:
            draw_entity(con, entity)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities): #Removes all entities one by one. Might become a source of performance issues.
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    libtcod.console_set_default_foreground(con, entity.color)
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)