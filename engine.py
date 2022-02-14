#for later "|"
import sys
import os
import numpy as np

os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import glob
import tcod as libtcod
from input_handler import handle_keys, handle_mouse, handle_main_menu
from render_functions import RenderOrder, clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_state import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message
from initialize_new_game import get_constants, get_game_variables
from data_loaders import save_game, load_game
from menus import main_menu, message_box
from random_utils import roll

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png") #Font/tileset
#TILE_FILE = os.path.join(DATA_FOLDER, "arial10x10.png")
BACKGROUND_FILE = os.path.join(DATA_FOLDER, "bground.jpg")


def main():
    print("#############################################")
    constants = get_constants()
        
    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    #libtcod.tileset.load_tilesheet(TILE_FILE, 16, 16, libtcod.tileset.CHARMAP_CP437)
    libtcod.console_init_root(constants["screen_width"], 
        constants["screen_height"], "libtcode game", False) # Configuring the game window/console

    con = libtcod.console_new(constants["screen_width"], constants["screen_height"]) #Initializing the game window/console
    panel = libtcod.console_new(constants["panel_width"]-30, constants["panel_height"]) #We initialize the UI panel
    other_bars = libtcod.console_new(12, 6)
    sidebar = libtcod.console_new(constants["sidebar_width"], constants["sidebar_height"])

    player = None
    cursor = None
    entities = []
    game_map = None
    message_log = None
    game_state = None
    name_list = constants["name_list"]

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load(BACKGROUND_FILE)

    key = libtcod.Key() #See if a key is pressed
    mouse = libtcod.Mouse() #See if mouse is used

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, 
                constants["screen_width"], constants["screen_height"])

            if show_load_error_message:
                message_box(con, "No save game to load", 50, constants["screen_width"], constants["screen_height"])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get("new_game")
            load_saved_game = action.get("load_game")
            exit_game = action.get("exit")

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state, name_list, cursor, name_part_list = get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state, name_list, cursor, name_part_list = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break
        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, 
                con, panel, sidebar, other_bars, constants, name_list, cursor, name_part_list)
            
            show_main_menu = True

def play_game(player, entities, game_map, message_log, game_state, con, panel, sidebar, other_bars, constants, name_list, cursor, name_part_list):
    fov_recompute = True #Do not recompute fov every frame. Just when changes happen.

    key = libtcod.Key() #See if a key is pressed
    mouse = libtcod.Mouse() #See if mouse is used

    fov_map = initialize_fov(game_map) #Initial state of the fov
    previous_game_state = game_state
    targeting_item = None
    draw_char_screen = True
    draw_entity_screen = False
    draw_eqp_screen = False
    analyzed_entity = None
    draw_stat_screen = False

    while not libtcod.console_is_window_closed(): #Main loop
        if fov_recompute: #Recomputes fov if needed
            recompute_fov(fov_map, player.x, player.y, constants["fov_radius"], constants["fov_light_walls"], constants["fov_algorithm"])
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse) #Check for keypresses

        render_all(con, panel, sidebar, other_bars, entities, player, game_map, fov_map, fov_recompute, message_log, constants["screen_width"], constants["screen_height"], 
            constants["bar_width"], constants["panel_height"], constants["panel_x"], constants["panel_y"], mouse, constants["colors"], game_state, cursor, draw_char_screen, analyzed_entity,
            draw_entity_screen, draw_eqp_screen, draw_stat_screen, constants["sidebar_width"], constants["sidebar_height"])
        libtcod.console_flush() #Updates to a newer version of the console, where blit has been drawing the new stuff

        clear_all(con, entities)
        
        #Input handling (using the input_handler.py file)
        action = handle_keys(key, game_state) 
        mouse_action = handle_mouse(mouse)

        move = action.get("move")
        wait = action.get("wait")
        pickup = action.get("pickup")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        inventory_index = action.get("inventory_index")
        take_stairs = action.get("take_stairs")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        level_up = action.get("level_up")
        show_character_screen = action.get("show_character_screen")
        cursor_move = action.get("cursor_move")
        chosen_target = action.get("chosen_target")
        look = action.get("look")
        look_cancel = action.get("look_cancel")
        look_at = action.get("look_at")
        show_entity_screen = action.get("show_entity_screen")
        message_archive = action.get("message_archive")
        show_eqp_screen = action.get("show_eqp_screen")
        show_stat_screen = action.get("show_stat_screen")
        center_map = action.get("center_map")
        
        left_click = mouse_action.get("left_click")
        right_click = mouse_action.get("right_click")

        #Player turn logic
        player_turn_results = []

        if show_entity_screen:
            if draw_entity_screen:
                draw_entity_screen = False
            else:
                draw_entity_screen = True
                if analyzed_entity == None:
                    analyzed_entity = player

        if show_eqp_screen:
            if draw_eqp_screen:
                draw_eqp_screen = False
            else:
                draw_eqp_screen = True
        
        if show_stat_screen:
            if draw_stat_screen:
                draw_stat_screen = False
            else:
                draw_stat_screen = True


        if look:
            previous_game_state = game_state
            game_state = GameStates.LOOK
            cursor.render_order = RenderOrder.UI
            cursor.x, cursor.y = player.x, player.y

        if look_cancel:
            cursor.render_order = RenderOrder.INVISIBLE
            game_state = previous_game_state

        if look_at:
            for entity in entities:
                if entity.x == cursor.x and entity.y == cursor.y and entity.render_order != RenderOrder.INVISIBLE:
                    if entity.fighter:
                        analyzed_entity = entity
                        draw_entity_screen = True

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                destination_x = player.x + dx
                destination_y = player.y + dy
                target = player.get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    if target.friendly:
                        if target not in player.followers:
                            talk_results = player.fighter.talk_with(target)
                            player_turn_results.extend(talk_results)
                        else:
                            player.move(dx, dy)
                    else:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                else:
                    fov_recompute = True
                    player.move(dx, dy)

            game_state = GameStates.ENEMY_TURN
        
        if cursor_move:
            dx, dy = cursor_move
            cursor.move(dx, dy)

        elif wait:
            game_state = GameStates.ENEMY_TURN

        if pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_items(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message("There is nothing here to pick up.", libtcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY
        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(
                    targeting_item,
                    entities=entities,
                    fov_map=fov_map,
                    target_x=target_x, target_y=target_y)

                player_turn_results.extend(item_use_results)
                cursor.render_order = RenderOrder.INVISIBLE
                game_state = previous_game_state
            elif right_click:
                cursor.render_order = RenderOrder.INVISIBLE
                game_state = previous_game_state

            elif chosen_target:
                cursor.render_order = RenderOrder.INVISIBLE
                target_x, target_y = cursor.x, cursor.y
                item_use_results = player.inventory.use(
                    targeting_item,
                    entities=entities,
                    fov_map=fov_map,
                    target_x=target_x, target_y=target_y)
                
                player_turn_results.extend(item_use_results)
                game_state = previous_game_state

        if level_up:
            if level_up == "con":
                player.fighter.character_sheet.constitution += 1
                player.fighter.base_max_hp += roll(1, 8)[0]
                if player.fighter.hp + player.fighter.character_sheet.ability_modifiers.get("con") <= player.fighter.max_hp:
                    player.fighter.hp += player.fighter.character_sheet.ability_modifiers.get("con")
                else:
                    player.fighter.hp = player.fighter.max_hp
                


            elif level_up == "str":
                player.fighter.character_sheet.strenght += 1
            elif level_up == "dex":
                player.fighter.character_sheet.dexterity += 1
            
            game_state = previous_game_state

        if show_character_screen:
            if draw_char_screen:
                draw_char_screen = False
            else:
                draw_char_screen = True
        
        if message_archive:
            previous_game_state = game_state
            game_state = GameStates.MESSAGE_ARCHIVE

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants, name_list, name_part_list, cursor)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(con)

                    break
            else:
                message_log.add_message(Message("There are no stairs here.", libtcod.yellow))

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        
        if center_map:
            game_map.center_map(player, entities)

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN, GameStates.MESSAGE_ARCHIVE):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({"targeting_canceled":True})
            else:
                save_game(player, entities, game_map, message_log, game_state, name_list, cursor, name_part_list)
                return True
        #After this the code handles the execution of things that happened on the player's turn.

        for player_turn_result in player_turn_results: 
            message = player_turn_result.get("message")
            dead_entity = player_turn_result.get("dead")
            item_added = player_turn_result.get("item_added")
            item_consumed = player_turn_result.get("consumed")
            item_dropped = player_turn_result.get("item_dropped")
            equip = player_turn_result.get("equip")
            targeting = player_turn_result.get("targeting")
            targeting_canceled = player_turn_result.get("targeting_canceled")
            xp = player_turn_result.get("xp")

            if message:
                message_log.add_message(message)
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN
            if item_consumed:
                game_state == GameStates.ENEMY_TURN
            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN
            if equip:
                equip_results = player.equipment.toggle_equip(equip)
                for equip_result in equip_results:
                    equipped = equip_result.get("equipped")
                    dequipped = equip_result.get("dequipped")
                    if equipped:
                        message_log.add_message(Message("You equipped the {}".format(equipped.name)))
                    if dequipped:
                        message_log.add_message(Message("You dequipped the {}".format(dequipped.name)))
                game_state = GameStates.ENEMY_TURN
            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                cursor.render_order = RenderOrder.UI
                cursor.x, cursor.y = player.x, player.y
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)
            if targeting_canceled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))
            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message("You gain {} experience points.".format(xp), 
                    libtcod.white))
                if leveled_up:
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP

                    message_log.add_message(Message("Your skills grow stronger! You reached level {}".format(
                        player.level.current_level), libtcod.yellow))

        #Enemy turn logic
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities) #Enemy takes their turn

                    for enemy_turn_result in enemy_turn_results: #Handles messages and death during enemy's turn
                        message = enemy_turn_result.get("message")
                        dead_entity = enemy_turn_result.get("dead")

                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)
                            
                            message_log.add_message(message)

                if game_state == GameStates.PLAYER_DEAD: #Apparently you need two of these here. Haven't bothered to investigate why, Probably to my own cost.
                    break            
            if game_state == GameStates.PLAYER_DEAD:
                break

            else:
                game_state = GameStates.PLAYERS_TURN

if __name__ == "__main__":
    main()