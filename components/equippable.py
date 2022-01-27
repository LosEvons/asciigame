from equipment_slots import EquipmentSlots


class Equippable:
    def __init__(self, slot, damage_dice=None, damage_bonus=0, ac_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.ac_bonus = ac_bonus
        self.max_hp_bonus = max_hp_bonus
        self.damage_dice = damage_dice
        self.damage_bonus = damage_bonus
