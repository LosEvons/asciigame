#for later "|"
import sys
import os

os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import glob
import tcod as libtcod
from input_handler import handle_keys, handle_mouse, handle_main_menu
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_state import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message
from initialize_new_game import get_constants, get_game_variables
from data_loaders import save_game, load_game
from menus import main_menu, message_box

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png") #Font/tileset
BACKGROUND_FILE = os.path.join(DATA_FOLDER, "bground.jpg")

def main():
    constants = get_constants()
        
    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    libtcod.console_init_root(constants["screen_width"], 
        constants["screen_height"], "libtcode game", False) # Configuring the game window/console

    con = libtcod.console_new(constants["screen_width"], constants["screen_height"]) #Initializing the game window/console
    panel = libtcod.console_new(constants["screen_width"], constants["panel_height"]) #We initialize the UI panel

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

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
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break
        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, 
                con, panel, constants)
            
            show_main_menu = True

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    fov_recompute = True #Do not recompute fov every frame. Just when changes happen.

    key = libtcod.Key() #See if a key is pressed
    mouse = libtcod.Mouse() #See if mouse is used

    fov_map = initialize_fov(game_map) #Initial state of the fov
    previous_game_state = game_state
    targeting_item = None

    while not libtcod.console_is_window_closed(): #Main loop
        if fov_recompute: #Recomputes fov if needed
            recompute_fov(fov_map, player.x, player.y, constants["fov_radius"], constants["fov_light_walls"], constants["fov_algorithm"])
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse) #Check for keypresses

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants["screen_width"], constants["screen_height"], 
            constants["bar_width"], constants["panel_height"], constants["panel_y"], mouse, constants["colors"], game_state)
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
        
        left_click = mouse_action.get("left_click")
        right_click = mouse_action.get("right_click")

        #Player turn logic
        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                destination_x = player.x + dx
                destination_y = player.y + dy
                target = player.get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    fov_recompute = True
                    player.move(dx, dy)

            game_state = GameStates.ENEMY_TURN

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
                game_state = previous_game_state
            elif right_click:
                game_state = previous_game_state

        if level_up:
            if level_up == "hp":
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == "str":
                player.fighter.base_power += 1
            elif level_up == "def":
                player.fighter.base_defense += 1
            
            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(con)

                    break
            else:
                message_log.add_message(Message("There are no stairs here.", libtcod.yellow))

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({"targeting_canceled":True})
            else:
                save_game(player, entities, game_map, message_log, game_state)


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

            if show_character_screen:
                previous_game_state = game_state
                game_state = GameStates.CHARACTER_SCREEN

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