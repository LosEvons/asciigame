import tcod as libtcod

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)

def message_archive_box(con, message_archive, screen_width, screen_height):
    window = libtcod.console_new(screen_width, screen_height)
    y = screen_height -2
    for message in message_archive:
        if y == 0:
            break

        libtcod.console_print_ex(window, 1, y, libtcod.BKGND_ALPHA(100), libtcod.LEFT, message.text)
        y -= 1
    
    libtcod.console_blit(window, 0, 0, screen_width, screen_height, 0, 0, 0, 1.0, 0.7)        

def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    options = [
        "Constitution ({}+1)".format(player.fighter.character_sheet.constitution),
        "Strength ({}+1)".format(player.fighter.character_sheet.strenght),
        "Dexterity ({}+1)".format(player.fighter.character_sheet.dexterity)
    ]

    menu(con, header, options, menu_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width/2), int(screen_height/2) - 4,
        libtcod.BKGND_NONE, libtcod.CENTER, "LOGUERIKE")
    libtcod.console_print_ex(0, int(screen_width/2), int(screen_height - 2),
        libtcod.BKGND_NONE, libtcod.CENTER, "By nsu")
    menu(con, '', ["play a new game", "Continue last game", "Quit"], 24, screen_width, screen_height)

def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26: raise ValueError("Cannot have a menu with more than 26 options")

    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    window = libtcod.console_new(width, height)


    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 1, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = "(" + chr(letter_index) + ") " + option_text
        libtcod.console_print_ex(window, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
    
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def inventory_menu(con, header, player, inventory_width, screen_width, screen_height):
    if len(player.inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = []
        handled_items = []

        for item in player.inventory.items:
            for key, value in player.equipment.bodyparts.items():
                if value == item:
                    if item.equippable.damage_dice:
                        handled_items.append(item)
                        options.append("{} {}d{}+{} (in {})".format(item.name, item.equippable.damage_dice[0], item.equippable.damage_dice[1], item.equippable.damage_bonus, key))
                    elif item.equippable.ac_bonus or item.equippable.max_hp_bonus:
                        handled_items.append(item)
                        options.append("{} +{}AC&+{}HP (in {})".format(item.name, item.equippable.ac_bonus, item.equippable.max_hp_bonus, key))

            if item not in handled_items and item.equippable:
                if item.equippable.damage_dice:
                    handled_items.append(item)
                    options.append("{} {}d{}+{}".format(item.name, item.equippable.damage_dice[0], item.equippable.damage_dice[1], item.equippable.damage_bonus))
                elif item.equippable.ac_bonus or item.equippable.max_hp_bonus:
                    handled_items.append(item)
                    options.append("{} +{}AC&+{}HP".format(item.name, item.equippable.ac_bonus, item.equippable.max_hp_bonus))
            
            elif item not in handled_items:
                handled_items.append(item)
                options.append(item.name)

    menu(con, header, options, inventory_width, screen_width, screen_height)

def character_screen(player, char_screen_width, char_screen_height, 
    screen_width, screen_height):

    window = libtcod.console_new(char_screen_width, char_screen_height)
    window.draw_frame(0, 0, char_screen_width, char_screen_height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Character Information")
    libtcod.console_print_rect_ex(window, 1, 2, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Level: {}".format(player.level.current_level))
    libtcod.console_print_rect_ex(window, 1, 3, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Experience: {}".format(player.level.current_xp))
    libtcod.console_print_rect_ex(window, 1, 4, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Experience to Level: {}".format(player.level.experience_to_next_level - player.level.current_xp))
    libtcod.console_print_rect_ex(window, 1, 5, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Max HP: {}".format(player.fighter.max_hp))
    if player.equipment.damage_dice != None:
        libtcod.console_print_rect_ex(window, 1, 6, char_screen_width, char_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Attack: {}d{}+{}".format(player.equipment.damage_dice[0], player.equipment.damage_dice[1], player.equipment.damage_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 6, char_screen_width, char_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Attack: {}d{}".format(player.fighter.unarmed_damage[0], player.fighter.unarmed_damage[1]))
        
    libtcod.console_print_rect_ex(window, 1, 7, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "AC: {}".format(player.fighter.ac))

    x = screen_width - char_screen_width
    y = screen_height - char_screen_height

    libtcod.console_blit(window, 0, 0, char_screen_width, char_screen_height,
        0, x, y, 1.0, 0.7)


def fighter_info_screen(entity, char_screen_width, char_screen_height, 
    screen_width, screen_height, draw_char_screen):

    window = libtcod.console_new(char_screen_width, char_screen_height)
    window.draw_frame(0, 0, char_screen_width, char_screen_height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Entity Information")
    libtcod.console_print_rect_ex(window, 1, 2, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Name: {}".format(entity.name))
    libtcod.console_print_rect_ex(window, 1, 3, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Max HP: {}".format(entity.fighter.max_hp))
    if entity.equipment and entity.equipment.damage_dice:
        libtcod.console_print_rect_ex(window, 1, 4, char_screen_width, char_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Attack: {}d{}+{}".format(entity.equipment.damage_dice[0], entity.equipment.damage_dice[1], entity.equipment.damage_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 4, char_screen_width, char_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Attack: {}d{}".format(entity.fighter.unarmed_damage[0], entity.fighter.unarmed_damage[1]))

    libtcod.console_print_rect_ex(window, 1, 5, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "AC: {}".format(entity.fighter.ac))

    if draw_char_screen:
        x = screen_width - char_screen_width
        y = screen_height - char_screen_height * 2
    else:
        x = screen_width - char_screen_width
        y = screen_height - char_screen_height

    libtcod.console_blit(window, 0, 0, char_screen_width, char_screen_height,
        0, x, y, 1.0, 0.7)

def equipment_info_screen(player, eqp_screen_width, eqp_screen_height, 
    screen_width, screen_height, draw_entity_screen, draw_character_screen, other_panel_height):

    window = libtcod.console_new(eqp_screen_width, eqp_screen_height)

    if draw_entity_screen and draw_character_screen:
        x = screen_width - eqp_screen_width
        y = 0
        eqp_screen_height -= other_panel_height * 2
    elif draw_entity_screen or draw_character_screen:
        x = screen_width - eqp_screen_width
        y = 0
        eqp_screen_height -= other_panel_height
    else:
        x = screen_width - eqp_screen_width
        y = 0
    
    window.draw_frame(0, 0, eqp_screen_width, eqp_screen_height)

    rows = 0
    for key, value in player.equipment.bodyparts.items():
        if value:
            if value.equippable and value.equippable.damage_dice:
                libtcod.console_print_rect_ex(window, 1, rows+1, eqp_screen_width, eqp_screen_height,
                    libtcod.BKGND_NONE, libtcod.LEFT, "{}: '{}'".format(key.capitalize(), value.name))
                libtcod.console_print_rect_ex(window, 3, rows+2, eqp_screen_width, eqp_screen_height,
                    libtcod.BKGND_NONE, libtcod.LEFT, "-{}d{}+{}".format(value.equippable.damage_dice[0], value.equippable.damage_dice[1], 
                    value.equippable.damage_bonus))
            else:
                libtcod.console_print_rect_ex(window, 1, rows+1, eqp_screen_width, eqp_screen_height,
                    libtcod.BKGND_NONE, libtcod.LEFT, "{}: '{}'".format(key.capitalize(), value.name))
                libtcod.console_print_rect_ex(window, 3, rows+2, eqp_screen_width, eqp_screen_height,
                    libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC&+{}HP".format(value.equippable.ac_bonus, value.equippable.max_hp_bonus))
            
            rows += 2

        libtcod.console_blit(window, 0, 0, eqp_screen_width, eqp_screen_height,
        0, x, y, 1.0, 0.7)
"""

    
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, eqp_screen_width, eqp_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Equipment")
    if player.equipment.head:
        libtcod.console_print_rect_ex(window, 1, 2, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Head: '{}'".format(player.equipment.head.name))
        libtcod.console_print_rect_ex(window, 3, 3, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.head.equippable.ac_bonus, player.equipment.head.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 2, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Head: None")

    if player.equipment.main_hand:
        libtcod.console_print_rect_ex(window, 1, 4, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Main-Hand: '{}'".format(player.equipment.main_hand.name))
        libtcod.console_print_rect_ex(window, 3, 5, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "-{}d{}+{}".format(player.equipment.main_hand.equippable.damage_dice[0],player.equipment.main_hand.equippable.damage_dice[1], 
            player.equipment.main_hand.equippable.damage_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 4, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Main-Hand: None")

    if player.equipment.off_hand:
        libtcod.console_print_rect_ex(window, 1, 6, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Off-Hand: {}".format(player.equipment.off_hand.name))
        libtcod.console_print_rect_ex(window, 3, 7, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.off_hand.equippable.ac_bonus, player.equipment.off_hand.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 6, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Off-Hand: None")

    if player.equipment.shoulders:
        libtcod.console_print_rect_ex(window, 1, 8, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Shoulders: {}".format(player.equipment.shoulders.name))
        libtcod.console_print_rect_ex(window, 3, 9, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.shoulders.equippable.ac_bonus,
            player.equipment.shoulders.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 8, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Shoulders: None")
    
    if player.equipment.shoulders:
        libtcod.console_print_rect_ex(window, 1, 10, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Chest: {}".format(player.equipment.chest.name))
        libtcod.console_print_rect_ex(window, 3, 11, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.chest.equippable.ac_bonus,
            player.equipment.chest.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 10, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Chest: None")

    if player.equipment.arms:
        libtcod.console_print_rect_ex(window, 1, 12, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Arms: {}".format(player.equipment.arms.name))
        libtcod.console_print_rect_ex(window, 3, 13, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.arms.equippable.ac_bonus,
            player.equipment.arms.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 12, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Arms: None")
    
    if player.equipment.right_hand:
        libtcod.console_print_rect_ex(window, 1, 14, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Ring: {}".format(player.equipment.right_hand.name))
        libtcod.console_print_rect_ex(window, 3, 15, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.right_arm.equippable.ac_bonus,
            player.equipment.right_arm.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 14, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Ring: None")
    
    if player.equipment.waist:
        libtcod.console_print_rect_ex(window, 1, 16, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Waist: {}".format(player.equipment.waist.name))
        libtcod.console_print_rect_ex(window, 3, 17, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.waist.equippable.ac_bonus,
            player.equipment.waist.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 16, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Waist: None")
    
    if player.equipment.legs:
        libtcod.console_print_rect_ex(window, 1, 18, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Legs: {}".format(player.equipment.legs.name))
        libtcod.console_print_rect_ex(window, 3, 19, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.legs.equippable.ac_bonus,
            player.equipment.legs.equippable.max_hp_bonus))
    else:
        libtcod.console_print_rect_ex(window, 1, 18, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Legs: None")

    if player.equipment.feet:
        libtcod.console_print_rect_ex(window, 1, 20, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Feet: {}".format(player.equipment.feet.name))
        libtcod.console_print_rect_ex(window, 3, 21, eqp_screen_width, eqp_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "+{}AC & +{}HP".format(player.equipment.bodyparts.feet.equippable.ac_bonus,
            player.equipment.bodyparts.feet.equippable.max_hp_bonus))


    libtcod.console_blit(window, 0, 0, eqp_screen_width, eqp_screen_height,
        0, x, y, 1.0, 0.7)"""