import tcod as libtcod
import math
import numpy as np
from enum import Enum
from game_state import GameStates
from menus import character_screen, equipment_info_screen, fighter_info_screen, inventory_menu, level_up_menu, message_archive_box, stat_info_screen

class RenderOrder(Enum):
    INVISIBLE = 1
    STAIRS = 2
    ITEM = 3
    CORPSE = 4
    ACTOR = 5
    UI = 6


def get_names_under_mouse(mouse, entities, fov_map, cursor,): #Displays the name of stuff under our mouse on the UI.
    (x1, y1, x2, y2) = (mouse.cx, mouse.cy, cursor.x, cursor.y) #Get mouse pos

    names = [entity.name for entity in entities
        if entity.x == (x1 or x2) and entity.y == (y1 or y2) and fov_map.fov[entity.y][entity.x] and entity is not cursor] #List of entity names if entities are visible and under our mouse
    names = ", ".join(names)

    return names.capitalize()

def render_sidebar(sidebar, player):
    sidebar.draw_frame(0, 0, sidebar.width, sidebar.height, fg=libtcod.white)
    bar_height = int(player.equipment.fuel / player.equipment.bodyparts["waist"].equippable.max_fuel * (sidebar.height-2))
    y = sidebar.height - bar_height - 1
    libtcod.console_set_default_background(sidebar, libtcod.darkest_orange)
    if bar_height > 0:
        libtcod.console_rect(sidebar, 1, y, sidebar.width-2, bar_height, False, libtcod.BKGND_SCREEN)

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color, game_map): #Render the HP bar
    panel.draw_frame(0, 0, panel.width, panel.height, fg=libtcod.white)
    panel.print_box(panel.width//2, 0, 34, 1, " Dungeon Level {} ".format(game_map.dungeon_level))
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

def render_enemy_bar(entities, fov_map, game_map, other_bars):
    bar_background = "----------"
    other_bars.draw_frame(0, 0, other_bars.width, other_bars.height)
    libtcod.console_set_default_background(other_bars, libtcod.black)
    count = 1
    for entity in entities:
        if entity.render_order != RenderOrder.INVISIBLE and entity.fighter and not entity.name == "Player" and not entity.friendly:
            if fov_map.fov[entity.y][entity.x]:
                libtcod.console_set_default_foreground(other_bars, libtcod.grey)
                libtcod.console_print_ex(other_bars, 1, count, libtcod.BKGND_NONE,
                    libtcod.LEFT, bar_background)
                hp_str = ""
                percentage = entity.fighter.hp / entity.fighter.max_hp
                hp_to_draw = int(np.ceil(percentage * 10))
                libtcod.console_set_default_foreground(other_bars, libtcod.red)
                for i in range (hp_to_draw):
                    hp_str += "O"

                libtcod.console_print_ex(other_bars, 1, count, libtcod.BKGND_NONE,
                    libtcod.LEFT, hp_str)
                count += 1
    

def render_all(con, map_console, panel, sidebar, other_bars, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
    screen_height, bar_width, panel_height, panel_x, panel_y, mouse, colors, game_state, cursor, draw_char_screen, analyzed_entity,
    draw_entity_screen, draw_eqp_screen, draw_stat_screen, sidebar_width, sidebar_height, map_x_anchor, map_y_anchor, lantern_color_map,
    lantern_in_use, grass_color_map, stone_color_map):

    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                libtcod.console_set_char_background(map_console, x, y, libtcod.black)

                visible = fov_map.fov[y][x]

                wall = game_map.tiles[x][y].wall
                hwall = game_map.tiles[x][y].hwall
                vwall = game_map.tiles[x][y].vwall
                brwall = game_map.tiles[x][y].brwall
                blwall = game_map.tiles[x][y].blwall
                trwall = game_map.tiles[x][y].trwall
                tlwall = game_map.tiles[x][y].tlwall

                door = game_map.tiles[x][y].door
                grass = game_map.tiles[x][y].grass
                floor = game_map.tiles[x][y].floor
                tree = game_map.tiles[x][y].tree
                shade = game_map.tiles[x][y].shade

                debug = game_map.tiles[x][y].debug
                debug2 = game_map.tiles[x][y].debug2
                if debug:
                    libtcod.console_set_char_background(map_console, x, y, libtcod.light_red, libtcod.BKGND_SET)
                if debug2:
                    libtcod.console_set_char_background(map_console, x, y, libtcod.light_green, libtcod.BKGND_SET)
                if visible:             #If it's visible (in the fov), draw it
                    if wall:
                        if game_map.tiles[x][y].color:
                            libtcod.console_set_default_foreground(map_console, game_map.tiles[x][y].color)
                        else:
                            from_noise_texture = int((game_map.stone_noise.get_point(x=x, y=y) + 1) * 100)
                            new_color = stone_color_map[from_noise_texture]
                            game_map.tiles[x][y].color = new_color
                            libtcod.console_set_default_foreground(map_console, new_color)
                        libtcod.console_put_char(map_console, x, y, '0', libtcod.BKGND_NONE)
                    elif hwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_gray, libtcod.BKGND_SET)
                        libtcod.console_put_char(map_console, x, y, 205, libtcod.BKGND_NONE)
                    elif vwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_gray, libtcod.BKGND_SET)
                        libtcod.console_put_char(map_console, x, y, 186, libtcod.BKGND_NONE)
                    elif brwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_gray, libtcod.BKGND_SET)
                        libtcod.console_put_char(map_console, x, y, 188, libtcod.BKGND_NONE)
                    elif trwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_gray, libtcod.BKGND_SET)
                        libtcod.console_put_char(map_console, x, y, 187, libtcod.BKGND_NONE)
                    elif blwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_gray, libtcod.BKGND_SET)
                        libtcod.console_put_char(map_console, x, y, 200, libtcod.BKGND_NONE)
                    elif tlwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_gray, libtcod.BKGND_SET)
                        libtcod.console_put_char(map_console, x, y, 201, libtcod.BKGND_NONE)
                    elif door:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_wall'))
                        libtcod.console_put_char(map_console, x, y, '+', libtcod.BKGND_NONE)
                    elif grass:
                        if game_map.tiles[x][y].color:
                            libtcod.console_set_default_foreground(map_console, game_map.tiles[x][y].color)
                        else:
                            from_noise_texture = int((game_map.grass_noise.get_point(x=x, y=y) + 1) * 100)
                            new_color = grass_color_map[from_noise_texture]
                            game_map.tiles[x][y].color = new_color
                            libtcod.console_set_default_foreground(map_console, new_color)
                        libtcod.console_put_char(map_console, x, y, 176, libtcod.BKGND_NONE)
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darker_green, libtcod.BKGND_ALPHA(230))
                    elif tree:
                        libtcod.console_set_default_foreground(map_console, libtcod.dark_orange)
                        libtcod.console_put_char(map_console, x, y, 'O', libtcod.BKGND_NONE)
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.dark_orange, libtcod.BKGND_ALPHA(230))
                    elif shade:
                        libtcod.console_set_default_foreground(map_console, libtcod.darker_green)
                        libtcod.console_put_char(map_console, x, y, 176, libtcod.BKGND_NONE)
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_green, libtcod.BKGND_ALPHA(100))
                    elif floor:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_ground'))
                        libtcod.console_put_char(map_console, x, y, '.', libtcod.BKGND_NONE)
                    else:
                        libtcod.console_set_default_foreground(map_console, colors.get('light_ground'))
                        libtcod.console_put_char(map_console, x, y, '.', libtcod.BKGND_NONE)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored: # If it has been seen previously, draw it but darker.
                    if wall:
                        #libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET) <-- Solid background
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, '0', libtcod.BKGND_NONE)
                    elif hwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, 205, libtcod.BKGND_NONE)
                    elif vwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, 186, libtcod.BKGND_NONE)
                    elif brwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, 188, libtcod.BKGND_NONE)
                    elif trwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, 187, libtcod.BKGND_NONE)
                    elif blwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, 200, libtcod.BKGND_NONE)
                    elif tlwall:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))
                        libtcod.console_put_char(map_console, x, y, 201, libtcod.BKGND_NONE)
                    elif door:
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_wall'))    
                        libtcod.console_put_char(map_console, x, y, '+', libtcod.BKGND_NONE)
                    elif grass:
                        libtcod.console_set_default_foreground(map_console, game_map.tiles[x][y].color*0.5)
                        libtcod.console_put_char(map_console, x, y, 176, libtcod.BKGND_NONE)
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_green, libtcod.BKGND_ALPHA(240))
                    elif tree:
                        libtcod.console_set_default_foreground(map_console, libtcod.dark_orange)
                        libtcod.console_put_char(map_console, x, y, 'O', libtcod.BKGND_NONE)
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_orange, libtcod.BKGND_ALPHA(240))
                    elif shade:
                        libtcod.console_set_default_foreground(map_console, libtcod.darkest_green)
                        libtcod.console_put_char(map_console, x, y, 176, libtcod.BKGND_NONE)
                        #libtcod.console_set_char_background(map_console, x, y, libtcod.darkest_green, libtcod.BKGND_ALPHA(100))
                    else:
                        #libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET) <-- Solid background
                        libtcod.console_set_default_foreground(map_console, colors.get('dark_ground'))
                        libtcod.console_put_char(map_console, x, y, '.', libtcod.BKGND_NONE)
                
                if lantern_in_use:
                    if visible:
                        if x < game_map.width and y < game_map.height:
                            dx = x - player.x
                            dy = y - player.y
                            distance = math.floor(math.sqrt(dx ** 2 + dy ** 2))
                            new_color = lantern_color_map[distance]
                            libtcod.console_set_char_background(map_console, x, y, new_color, libtcod.BKGND_ALPHA(100))

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    
    for entity in entities_in_render_order:         # Draw all entities in the list
        if entity.render_order != RenderOrder.INVISIBLE:
            if fov_map.fov[entity.y][entity.x] or (entity.stairs and game_map.tiles[entity.x][entity.y].explored): #If it's in our fov-range
                draw_entity(map_console, entity)
        if entity.name == "Cursor" and entity.render_order == RenderOrder.ACTOR:
            draw_entity(map_console, entity)

    libtcod.console_set_default_background(panel, libtcod.black)#Sets the UI background as black
    libtcod.console_clear(panel) #Clears UI before drawing it again
    libtcod.console_clear(sidebar)

    render_sidebar(sidebar, player)

    render_bar(panel, 1, 1, bar_width, "HP", player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_grey, game_map) #Draws the hp bar

    render_enemy_bar(entities, fov_map, game_map, other_bars)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, 2, 6, libtcod.BKGND_NONE, libtcod.LEFT,  #Draws stuff in the ui when enemy is moused over
        get_names_under_mouse(mouse, entities, fov_map, cursor))

    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color) #Draws messages in the UI, and y makes sure older messages get removed and messages stack
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0) #Blit draws stuff onto a hypothetical console. Flushing updates to the newer console.
    libtcod.console_blit(map_console, 0, 0, game_map.width, game_map.height, 0, map_x_anchor, map_y_anchor)
    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, panel_x, panel_y) #Draws our UI element into the console
    libtcod.console_blit(other_bars, 0, 0, 30, 30, 0, 15, 0)
    libtcod.console_blit(sidebar, 0, 0, sidebar_width, sidebar_height, 0, 0, 0)

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

    if draw_char_screen:
        character_screen(player, 30, panel_height, screen_width, screen_height)
    
    if draw_entity_screen:
        if analyzed_entity.render_order == RenderOrder.CORPSE:
            fighter_info_screen(player, 30, panel_height, screen_width, screen_height, draw_char_screen)
        else:
            fighter_info_screen(analyzed_entity, 30, panel_height, screen_width, screen_height, draw_char_screen)

    if game_state == GameStates.MESSAGE_ARCHIVE:
        message_archive_box(con, message_log.message_archive, screen_width, screen_height)
    
    if draw_eqp_screen:
        equipment_info_screen(player, 30, screen_height, screen_width, screen_height, 
            draw_entity_screen, draw_char_screen, panel_height)
    
    if draw_stat_screen:
        stat_info_screen(player, 30, screen_height, screen_width, screen_height, draw_entity_screen, 
            draw_char_screen, draw_eqp_screen, panel_height)


def clear_all(con, entities): #Removes all entities one by one. Might become a source of performance issues. Otherwise we'd also see the previously drawn entities, and this would become an mspaint knockoff.
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity): 
    libtcod.console_set_default_foreground(con, entity.color) #Set the color of our entity
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE) #Set the character/texture for our character


def clear_entity(con, entity): #Takes an entity's position, and draws a white space in it's stead
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
