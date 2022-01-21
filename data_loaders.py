import shelve
import os

SAVE_GAME = "savegame"

def save_game(player, entities, game_map, message_log, game_state, name_list, cursor):
    with shelve.open(SAVE_GAME, 'n') as data_file:
        data_file["player_index"] = entities.index(player)
        data_file["cursor_index"] = entities.index(cursor)
        data_file["entities"] =  entities
        data_file["game_map"] = game_map
        data_file["message_log"] = message_log
        data_file["game_state"] = game_state
        data_file["name_list"] = name_list

def load_game():
    if not os.path.isfile(SAVE_GAME + ".dat"):
        raise FileNotFoundError

    with shelve.open(SAVE_GAME, 'r') as data_file:
        player_index = data_file["player_index"]
        cursor_index = data_file["cursor_index"]
        entities = data_file["entities"]
        game_map = data_file["game_map"]
        message_log = data_file["message_log"]
        game_state = data_file["game_state"]
        name_list = data_file["name_list"]
        cursor = data_file["cursor"]
    
    player = entities[player_index]
    cursor = entities[cursor_index]

    return player, entities, game_map, message_log, game_state, name_list, cursor