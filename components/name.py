from asyncio import shield
from random import choice

def Name(name_list, type):
    if type == "goblin":
        goblin_names = name_list.get("goblin_names")
        chosen_name = choice(goblin_names)
        #goblin_names.remove(chosen_name)
        #name_list["goblin_names"] = goblin_names
        return chosen_name

    elif type == "hydra":
        hydra_names = name_list.get("hydra_names")
        chosen_name = choice(hydra_names)
        #hydra_names.remove(chosen_name)
        #name_list["hydra_names"] = hydra_names
        return chosen_name

    elif type == "shield":
        shield_names = name_list.get("shield_names")
        chosen_name = choice(shield_names)
        #shield_names.remove(chosen_name)
        #name_list["shield_names"] = shield_names
        return chosen_name

    elif type == "sword":
        sword_names = name_list.get("sword_names")
        chosen_name = choice(sword_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name
    
    elif type == "helmet":
        helmet_names = name_list.get("helmet_names")
        chosen_name = choice(helmet_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name

    elif type == "shoulderpads":
        shoulderpad_names = name_list.get("shoulderpad_names")
        chosen_name = choice(shoulderpad_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name

    elif type == "chestplate":
        chestplate_names = name_list.get("chestplate_names")
        chosen_name = choice(chestplate_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name
    
    elif type == "armguards":
        armguard_names = name_list.get("armguard_names")
        chosen_name = choice(armguard_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name
    
    elif type == "belt":
        belt_names = name_list.get("belt_names")
        chosen_name = choice(belt_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name
    
    elif type == "bracers":
        bracer_names = name_list.get("bracer_names")
        chosen_name = choice(bracer_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name
    
    elif type == "boots":
        boot_names = name_list.get("boot_names")
        chosen_name = choice(boot_names)
        #sword_names.remove(chosen_name)
        #name_list["sword_names"] = sword_names
        return chosen_name



def name_from_parts(name_part_list):
    first_names = name_part_list.get("first_names")
    first_name = choice(first_names)

    first_syllable = choice(name_part_list.get("syllables"))
    second_syllable = choice(name_part_list.get("syllables"))
    connector = choice(name_part_list.get("consonants"))

    surname = first_syllable + connector + second_syllable
    final_name = first_name + " " + surname.capitalize()
    
    return final_name