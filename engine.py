#for later "|"
import sys
import os

os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import glob
import tcod as libtcod
from entity import Entity
from input_handler import handle_keys, handle_mouse
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_state import GameStates
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message
from components.inventory import Inventory

DATA_FOLDER = "data"
FONT_FILE = os.path.join(DATA_FOLDER, "arial10x10.png") #Font/tileset

def main():
    screen_width = 80 #Screen size
    screen_height = 50
    map_width = 80 #Map size
    map_height = 45
    #Map generation parameters
    room_max_size = 10     
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    max_items_per_room = 2

    fov_algorithm = 2 #FOV-algorithm used - http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds
    fov_light_walls = True #Is FOV used to affect the visibility of things
    fov_radius = 10 

    bar_width = 20
    panel_height = 7                        #Player health bar properties
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2    #Message feed properties
    message_height = panel_height - 1

    #Some colors for current and later use
    colors = {
       'dark_wall': libtcod.Color(50, 50, 50),
       'dark_ground': libtcod.Color(50, 50, 50),
       'light_wall': libtcod.Color(255, 255, 255),
       'light_ground': libtcod.Color(100, 100, 100)
   }

    fov_recompute = True #Do not recompute fov every frame. Just when changes happen.
    fighter_component = Fighter(hp=30, defense=2, power=5) #Basically creates a fighter class. Is responsible for the different attributes
    inventory_component = Inventory(26) #We declare the size of a certain type of inventory
    player = Entity(int(screen_width / 2), int(screen_height/2), '@', libtcod.red, "Player", blocks=True, render_order=RenderOrder.ACTOR, 
        fighter=fighter_component, inventory=inventory_component) #Initializing the player
    entities = [player] #List of all the entities
    game_map = GameMap(map_width, map_height) #Initialize the game map
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, 
        max_monsters_per_room, max_items_per_room) #Generate the map

    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    libtcod.console_init_root(screen_width, screen_height, "libtcode game", False) # Configuring the game window/console
    con = libtcod.console_new(screen_width, screen_height) #Initializing the game window/console
    panel = libtcod.console_new(screen_width, panel_height) #We initialize the UI panel

    key = libtcod.Key() #See if a key is pressed
    mouse = libtcod.Mouse() #See if mouse is used

    fov_map = initialize_fov(game_map) #Initial state of the fov
    message_log = MessageLog(message_x, message_width, message_height)
    game_state = GameStates.PLAYERS_TURN #Gives the initiative to the player
    previous_game_state = game_state
    targeting_item = None

    while not libtcod.console_is_window_closed(): #Main loop
        if fov_recompute: #Recomputes fov if needed
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse) #Check for keypresses

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, 
            bar_width, panel_height, panel_y, mouse, colors, game_state)
        libtcod.console_flush() #Updates to a newer version of the console, where blit has been drawing the new stuff

        clear_all(con, entities)
        
        #Input handling (using the input_handler.py file)
        action = handle_keys(key, game_state) 
        mouse_action = handle_mouse(mouse)

        move = action.get("move")
        pickup = action.get("pickup")
        show_inventory = action.get("show_inventory")
        drop_inventory = action.get("drop_inventory")
        inventory_index = action.get("inventory_index")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        
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

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            else:
                return True
        #After this the code handles the execution of things that happen on the player's turn.

        for player_turn_result in player_turn_results: 
            message = player_turn_result.get("message")
            dead_entity = player_turn_result.get("dead")
            item_added = player_turn_result.get("item_added")
            item_consumed = player_turn_result.get("consumed")
            item_dropped = player_turn_result.get("item_dropped")
            targeting = player_turn_result.get("targeting")

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
            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)

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