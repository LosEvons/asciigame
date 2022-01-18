#for later "|"
import sys
import os

os.environ["path"] = os.path.dirname(sys.executable) + ";" + os.environ["path"] # does shit if you have multiple python versions installed.
import glob
import tcod as libtcod
from entity import Entity
from input_handler import handle_keys
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_state import GameStates
from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from game_messages import MessageLog

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
    player = Entity(int(screen_width / 2), int(screen_height/2), '@', libtcod.red, "Player", blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component) #Initializing the player
    entities = [player] #List of all the entities
    game_map = GameMap(map_width, map_height) #Initialize the game map
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room) #Generate the map

    libtcod.console_set_custom_font(FONT_FILE, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD) #Configuring the font
    libtcod.console_init_root(screen_width, screen_height, "libtcode game", False) # Configuring the game window/console
    con = libtcod.console_new(screen_width, screen_height) #Initializing the game window/console
    panel = libtcod.console_new(screen_width, panel_height)

    key = libtcod.Key() #See if a key is pressed
    mouse = libtcod.Mouse() #See if mouse is used

    fov_map = initialize_fov(game_map) #Initial state of the fov
    message_log = MessageLog(message_x, message_width, message_height)
    game_state = GameStates.PLAYERS_TURN #Gives the initiative to the player

    while not libtcod.console_is_window_closed(): #Main loop
        if fov_recompute: #Recomputes fov if needed
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse) #Check for keypresses

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, 
            bar_width, panel_height, panel_y, mouse, colors)
        libtcod.console_flush() #Updates to a newer version of the console, where blit has been drawing the new stuff

        clear_all(con, entities)
        
        #Movement handling (using the input_handler.py file)
        action = handle_keys(key)           

        move = action.get("move")
        exit = action.get("exit")
        fullscreen = action.get("fullscreen")
        
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

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if exit:
            return True

        for player_turn_result in player_turn_results:
            message = player_turn_result.get("message")
            dead_entity = player_turn_result.get("dead")
            if message:
                message_log.add_message(message)
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                
                message_log.add_message(message)

        #Enemy turn logic
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
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

                if game_state == GameStates.PLAYER_DEAD:
                    break            
            if game_state == GameStates.PLAYER_DEAD:
                break

            else:
                game_state = GameStates.PLAYERS_TURN

if __name__ == "__main__":
    main()