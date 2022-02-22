from equipment_slots import Bodyparts, EquipmentSlots

class Equipment():
    def __init__(self, bodyparts=Bodyparts):
        self.bodyparts = bodyparts.parts

    @property
    def max_hp_bonus(self):
        bonus = 0
        for key, value in self.bodyparts.items():
            if value and value.equippable:
                bonus += value.equippable.max_hp_bonus
        return bonus

    @property
    def ac_bonus(self):
        bonus = 0
        for key, value in self.bodyparts.items():
            if value and value.equippable:
                bonus = value.equippable.max_hp_bonus
        
        return bonus

    @property
    def damage_dice(self):
        damage_dice = None
        for key, value in self.bodyparts.items():
            if value and value.equippable and value.equippable.damage_dice:
                damage_dice = value.equippable.damage_dice
        return damage_dice

    @property
    def damage_bonus(self):
        damage_bonus = 0
        for key, value in self.bodyparts.items():
            if value and value.equippable and value.equippable.damage_bonus:
                damage_bonus += value.equippable.damage_bonus

        return damage_bonus
    
    @property
    def fuel(self):
        fuel = 0
        for key, value in self.bodyparts.items():
            if value and value.equippable and value.equippable.fuel:
                fuel += value.equippable.fuel
        
        return fuel

    def toggle_equip(self, equippable_entity):
        
        key_list = list(self.bodyparts.keys())
        value_list = list(self.bodyparts.values())

        results = []

        slot = equippable_entity.equippable.slot

        for slots in EquipmentSlots:
            slot_index = slots.value-1
            part = value_list[slot_index]
            if slot == slots:
                if part == equippable_entity:
                    self.bodyparts[key_list[slot_index]] = None
                    results.append({"dequipped":equippable_entity})
                else:
                    if part:
                        results.append({"dequipped":part})
                    self.bodyparts[key_list[slot_index]] = equippable_entity
                    results.append({"equipped":equippable_entity})

        return results