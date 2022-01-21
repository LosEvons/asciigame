import tcod as libtcod
from game_messages import Message
from random_utils import roll

class Fighter:
    def __init__(self, character_sheet, xp=0):
        self.character_sheet = character_sheet
        if self.character_sheet:
            self.character_sheet.owner = self
        self.base_max_hp = 8 + character_sheet.ability_modifiers.get("con")
        self.hp = self.base_max_hp
        self.base_ac = 10 + character_sheet.ability_modifiers.get("dex")
        self.xp = xp
        self.unarmed_damage = [1, 4]

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        
        return self.base_max_hp + bonus

    @property
    def damage_dice(self):
        if self.owner and self.owner.equipment:
            amount, sides = self.owner.equipment.damage_dice
            damage_roll = sum(roll(amount, sides)) + self.owner.equipment.damage_bonus
        else:
            amount, sides = self.unarmed_damage
            damage_roll = sum(roll(amount, sides))

        return damage_roll

    @property
    def ac(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.ac_bonus
        else:
            bonus = 0
        
        return self.base_ac + bonus

    def take_damage(self, amount): #Player takes damage. Pretty simple math, and a check for 0hp
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append ({"dead":self.owner, "xp":self.xp})
        
        return results

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        attack_roll = sum(roll(1, 20))

        if attack_roll >= target.fighter.ac:
            results.append({"message":Message("HIT: {} -> {} --to hit-> {} -> {}".format(
                self.owner.name, attack_roll, target.fighter.ac, target.name))})
            damage = self.damage_dice

            if damage > 0:
                results.append({
                    "message":Message("{} -> {} --damage-> {} - {}".format(
                        self.owner.name.capitalize(), damage, target.name, target.fighter.hp), libtcod.white)})
                results.extend(target.fighter.take_damage(damage))
            else:
                results.append({
                    "message":Message("{} -> {} --damage-> {} - {}".format(
                        self.owner.name.capitalize(), damage, target.name, target.fighter.hp), libtcod.white)})

        else:
            results.append({"message":Message("MISS: {} -> {} --to hit-> {} -> {}.".format(
                self.owner.name, attack_roll, target.name, target.fighter.ac))})
        
        return results