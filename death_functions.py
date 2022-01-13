import tcod as libtcod

from game_state import GameStates

def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red
    return "You died!", GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = "{} is dead!".format(monster.name.capitalize())

    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = "Remains of " + monster.name

    return death_message
