from enum import Enum
#Used to keep track of a turn system and initiative
class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3