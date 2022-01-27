from equipment_slots import EquipmentSlots


class Equippable:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

class Equippable2:
    def __init__(self, sword=None, shield=None, helmet=None, shoulderpads=None,
        chestplate=None, armguards=None, ring=None, belt=None, bracers=None, boots=None):
        if sword:
            self.slot = EquipmentSlots.MAIN_HAND
        #elif shield: