import tcod as libtcod

from game_state import GameStates
from render_functions import RenderOrder
from game_messages import Message

def kill_player(player): #Kills player. Currently just closes the console though.
    player.char = '%'
    player.color = libtcod.dark_red
    return Message("You died!", libtcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster): #Kills the monster. Changes character, render order, name, etc.
    death_message = Message("{} is dead!".format(monster.name.capitalize()), libtcod.orange)

    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = "Remains of " + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message
