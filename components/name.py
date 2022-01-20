from asyncio import shield
from random import choice

def Name(name_list, type):
    if type == "goblin":
        goblin_names = name_list.get("goblin_names")
        chosen_name = choice(goblin_names)
        name_list["goblin_names"] = goblin_names
        return chosen_name

    elif type == "hydra":
        hydra_names = name_list.get("hydra_names")
        chosen_name = choice(hydra_names)
        hydra_names.remove(chosen_name)
        name_list["hydra_names"] = hydra_names
        return chosen_name

    elif type == "shield":
        shield_names = name_list.get("shield_names")
        chosen_name = choice(shield_names)
        shield_names.remove(chosen_name)
        name_list["shield_names"] = shield_names
        return chosen_name

    elif type == "sword":
        sword_names = name_list.get("sword_names")
        chosen_name = choice(sword_names)
        sword_names.remove(chosen_name)
        name_list["sword_names"] = sword_names
        return chosen_name