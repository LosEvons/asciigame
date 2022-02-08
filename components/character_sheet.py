import numpy as np

class CharacterSheet:
    def __init__(self, strenght, constitution, dexterity, intelligence, wisdom, charisma):
        self.strenght = strenght
        self.constitution = constitution
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.ability_scores = {"str":self.strenght, "con":self.constitution, "dex":self.dexterity, "int":self.intelligence, "wis":self.wisdom, "cha":self.charisma}

    @property
    def ability_modifiers(self):
        ability_modifiers = {}
        for score, value in self.ability_scores.items():
            modifier = int(np.floor((value - 10) / 2))
            ability_modifiers.update({score:modifier})

        return ability_modifiers