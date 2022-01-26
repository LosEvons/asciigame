from enum import Enum
#keeps track of game state. What is active, and what is not.
class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    SHOW_INVENTORY = 4
    DROP_INVENTORY = 5
    TARGETING = 6
    LEVEL_UP = 7
    CHARACTER_SCREEN = 8
    LOOK = 9
    LOOK_AT = 10
    MESSAGE_ARCHIVE = 11