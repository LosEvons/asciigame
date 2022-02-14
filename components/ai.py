from re import I
import tcod as libtcod

from random import randint
from game_messages import Message

class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner
        results = []
        if fov_map.fov[monster.y][monster.x]:
            if monster.distance_to(target) >= 2: #Minimum distance 2, including the enemy's and its own square
                monster.move_astar(target, entities, game_map) #Moves with the A* algorithm

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target) #Automatically attacks the target
                results.extend(attack_results)

        return results

class ConfusedMonster:
    def __init__ (self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

                self.number_of_turns -= 1
        
        else:
            self.owner.ai = self.previous_ai
            results.append({"message":Message("The {} is no longer confused".format(self.owner.name), libtcod.red)})
        
        return results

class PartyMember:
    def __init__ (self, player):
        self.parent_previous_coordinates = None
        self.parent_current_coordinates = (player.x, player.y)

    def take_turn(self, player, fov_map, game_map, entities):        
        results = []
        party_member = self.owner

        self.parent_previous_coordinates = self.parent_current_coordinates
        self.parent_current_coordinates = (player.x, player.y)

        if self.parent_previous_coordinates != self.parent_current_coordinates:
            party_member.x = self.parent_previous_coordinates[0]
            party_member.y = self.parent_previous_coordinates[1]
        else:
            self.parent_current_coordinates = (player.x, player.y)
        
        return results

class PassiveNPC:
    def take_turn(self, player, fov_map, game_map, entities):
        return []