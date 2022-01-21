from equipment_slots import EquipmentSlots

class Equipment:
    def __init__(self, main_hand=None, off_hand=None):
        self.main_hand = main_hand
        self.off_hand = off_hand

    @property
    def max_hp_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus
        
        return bonus

    @property
    def ac_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.ac_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.ac_bonus
        
        return bonus

    @property
    def damage_dice(self):
        damage_dice = 0

        if self.main_hand and self.main_hand.equippable:
            damage_dice = self.main_hand.equippable.damage_dice

        if self.off_hand and self.off_hand.equippable:
            damage_dice = self.off_hand.equippable.damage_dice
        
        return damage_dice

    @property
    def damage_bonus(self):
        damage_bonus = 0

        if self.main_hand and self.main_hand.equippable:
            damage_bonus = self.main_hand.equippable.damage_bonus

        if self.off_hand and self.off_hand.equippable:
            damage_bonus = self.off_hand.equippable.damage_bonus
        
        return damage_bonus


    def toggle_equip(self, equippable_entity):
        results = []

        slot = equippable_entity.equippable.slot
    
        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({"dequipped":equippable_entity})
            else:
                if self.main_hand:
                    results.append({"dequipped":self.main_hand})
                self.main_hand = equippable_entity
                results.append({"equipped":equippable_entity})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({"dequipped":equippable_entity})
            else:
                if self.off_hand:
                    results.append({"dequipped":self.off_hand})
                self.off_hand = equippable_entity
                results.append({"equipped":equippable_entity})
        
        return results
