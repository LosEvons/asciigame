import tcod as libtcod
from enum import Enum
from game_state import GameStates
from menus import character_screen, fighter_info_screen, inventory_menu, level_up_menu, message_archive_box

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
        if entity.render_order != RenderOrder.INVISIBLE and entity.fighter and not entity.name == "Player":
            if fov_map.fov[entity.y][entity.x]:
                libtcod.console_set_default_foreground(other_bars, libtcod.grey)
                libtcod.console_print_ex(other_bars, 1, count, libtcod.BKGND_NONE,
                    libtcod.LEFT, bar_background)
                hp_str = ""
                percentage = entity.fighter.hp / entity.fighter.max_hp
                hp_to_draw = int(percentage * 10)
                libtcod.console_set_default_foreground(other_bars, libtcod.red)
                for i in range (hp_to_draw):
                    hp_str += "O"

                libtcod.console_print_ex(other_bars, 1, count, libtcod.BKGND_NONE,
                    libtcod.LEFT, hp_str)
                count += 1
    

def render_all(con, panel, other_bars, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, 
    screen_height, bar_width, panel_height, panel_y, mouse, colors, game_state, cursor, draw_char_screen, analyzed_entity,
    draw_entity_screen):
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
        if entity.render_order != RenderOrder.INVISIBLE:
            if fov_map.fov[entity.y][entity.x] or (entity.stairs and game_map.tiles[entity.x][entity.y].explored): #If it's in our fov-range
                draw_entity(con, entity)
        if entity.name == "Cursor" and entity.render_order == RenderOrder.ACTOR:
            draw_entity(con, entity)

    libtcod.console_set_default_background(panel, libtcod.black)#Sets the UI background as black
    libtcod.console_clear(panel) #Clears UI before drawing it again

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
    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y) #Draws our UI element into the console
    libtcod.console_blit(other_bars, 0, 0, 30, 30, 0, 0, 0)

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


def clear_all(con, entities): #Removes all entities one by one. Might become a source of performance issues. Otherwise we'd also see the previously drawn entities, and this would become an mspaint knockoff.
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity): 
    libtcod.console_set_default_foreground(con, entity.color) #Set the color of our entity
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE) #Set the character/texture for our character


def clear_entity(con, entity): #Takes an entity's position, and draws a white space in it's stead
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)