from equipment_slots import EquipmentSlots

class Equipment:
    def __init__(self, main_hand=None, off_hand=None, head=None, shoulders=None, chest=None, 
        arms=None, right_hand=None, left_hand=None, waist=None, legs=None, feet=None):
        self.main_hand = main_hand
        self.off_hand = off_hand
        self.head = head
        self.shoulders = shoulders
        self.chest = chest
        self.arms = arms
        self.right_hand = right_hand
        self.left_hand = left_hand
        self.waist = waist
        self.legs = legs
        self.feet = feet

    @property
    def max_hp_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus

        if self.head and self.head.equippable:
            bonus += self.head.equippable.max_hp_bonus
        
        if self.shoulders and self.shoulders.equippable:
            bonus += self.shoulders.equippable.max_hp_bonus
        
        if self.chest and self.chest.equippable:
            bonus += self.chest.equippable.max_hp_bonus
        
        if self.chest and self.arms.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus
        
        if self.right_hand and self.right_hand.equippable:
            bonus += self.right_hand.equippable.max_hp_bonus
        
        if self.left_hand and self.left_hand.equippable:
            bonus += self.left_hand.equippable.max_hp_bonus
        
        if self.waist and self.waist.equippable:
            bonus += self.waist.equippable.max_hp_bonus
        
        if self.legs and self.legs.equippable:
            bonus += self.legs.equippable.max_hp_bonus
        
        if self.feet and self.feet.equippable:
            bonus += self.feet.equippable.max_hp_bonus

        return bonus

    @property
    def ac_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.ac_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.ac_bonus
        
        if self.head and self.head.equippable:
            bonus += self.head.equippable.ac_bonus
        
        if self.shoulders and self.shoulders.equippable:
            bonus += self.shoulders.equippable.ac_bonus
        
        if self.chest and self.chest.equippable:
            bonus += self.chest.equippable.ac_bonus
        
        if self.chest and self.arms.equippable:
            bonus += self.off_hand.equippable.ac_bonus
        
        if self.right_hand and self.right_hand.equippable:
            bonus += self.right_hand.equippable.ac_bonus
        
        if self.left_hand and self.left_hand.equippable:
            bonus += self.left_hand.equippable.ac_bonus
        
        if self.waist and self.waist.equippable:
            bonus += self.waist.equippable.ac_bonus
        
        if self.legs and self.legs.equippable:
            bonus += self.legs.equippable.ac_bonus
        
        if self.feet and self.feet.equippable:
            bonus += self.feet.equippable.ac_bonus
        
        return bonus

    @property
    def damage_dice(self):
        damage_dice = None

        if self.main_hand and self.main_hand.equippable and self.main_hand.equippable.damage_dice:
            damage_dice = self.main_hand.equippable.damage_dice

        if self.off_hand and self.off_hand.equippable and self.off_hand.equippable.damage_dice:
            damage_dice = self.off_hand.equippable.damage_dice
        
        if self.head and self.head.equippable and self.head.equippable.damage_dice:
            damage_dice = self.head.equippable.damage_dice
        
        if self.shoulders and self.shoulders.equippable and self.shoulders.equippable.damage_dice:
            damage_dice = self.shoulders.equippable.damage_dice
        
        if self.chest and self.chest.equippable and self.chest.equippable.damage_dice:
            damage_dice = self.chest.equippable.damage_dice
        
        if self.chest and self.arms.equippable and self.arms.equippable.damage_dice:
            damage_dice = self.off_hand.equippable.damage_dice
        
        if self.right_hand and self.right_hand.equippable and self.right_hand.equippable.damage_dice:
            damage_dice = self.right_hand.equippable.damage_dice
        
        if self.left_hand and self.left_hand.equippable and self.left_hand.equippable.damage_dice:
            damage_dice = self.left_hand.equippable.damage_dice
        
        if self.waist and self.waist.equippable and self.waist.equippable.damage_dice:
            damage_dice = self.waist.equippable.damage_dice
    
        if self.legs and self.legs.equippable and self.legs.equippable.damage_dice:
            damage_dice = self.legs.equippable.damage_dice
        
        if self.feet and self.feet.equippable and self.feet.equippable.damage_dice:
            damage_dice = self.feet.equippable.damage_dice
        
        return damage_dice

    @property
    def damage_bonus(self):
        damage_bonus = 0

        if self.main_hand and self.main_hand.equippable:
            damage_bonus += self.main_hand.equippable.damage_bonus

        if self.off_hand and self.off_hand.equippable:
            damage_bonus += self.off_hand.equippable.damage_bonus
        
        if self.head and self.head.equippable:
            damage_bonus += self.head.equippable.damage_bonus
        
        if self.shoulders and self.shoulders.equippable:
            damage_bonus += self.shoulders.equippable.damage_bonus
        
        if self.chest and self.chest.equippable:
            damage_bonus += self.chest.equippable.damage_bonus
        
        if self.chest and self.arms.equippable:
            damage_bonus += self.off_hand.equippable.damage_bonus
        
        if self.right_hand and self.right_hand.equippable:
            damage_bonus += self.right_hand.equippable.damage_bonus
        
        if self.left_hand and self.left_hand.equippable:
            damage_bonus += self.left_hand.equippable.damage_bonus
        
        if self.waist and self.waist.equippable:
            damage_bonus += self.waist.equippable.damage_bonus
        
        if self.legs and self.legs.equippable:
            damage_bonus += self.legs.equippable.damage_bonus
        
        if self.feet and self.feet.equippable:
            damage_bonus += self.feet.equippable.damage_bonus
        
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
        elif slot == EquipmentSlots.HEAD:
            if self.head == equippable_entity:
                self.head = None
                results.append({"dequipped":equippable_entity})
            else:
                if self.head:
                    results.append({"dequipped":self.head})
                self.head = equippable_entity
                results.append({"equipped":equippable_entity})

        
        return results
