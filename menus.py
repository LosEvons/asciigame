import tcod as libtcod

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)

def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    options = [
        "Constitution (+20 HP, from {})".format(player.fighter.max_hp),
        "Strenght (+1 attack, from {})".format(player.fighter.power),
        "Agility (+1 defense, from {})".format(player.fighter.defense)
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
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = "(" + chr(letter_index) + ") " + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
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
        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append("{} (on main hand)".format(item.name))
            elif player.equipment.off_hand == item:
                options.append("{} (on off hand)".format(item.name))
            else:
                options.append(item.name)
        #options = [item.name for item in inventory.items]

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
    if player.equipment:
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
    screen_width, screen_height):

    window = libtcod.console_new(char_screen_width, char_screen_height)
    window.draw_frame(0, 0, char_screen_width, char_screen_height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 1, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Character Information")
    libtcod.console_print_rect_ex(window, 0, 2, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "Max HP: {}".format(entity.fighter.max_hp))
    if entity.equipment:
        libtcod.console_print_rect_ex(window, 0, 3, char_screen_width, char_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Attack: {}d{}+{}".format(entity.equipment.damage_dice[0], entity.equipment.damage_dice[1], entity.equipment.damage_bonus))
    else:
        libtcod.console_print_rect_ex(window, 0, 3, char_screen_width, char_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, "Attack: {}d{}".format(entity.fighter.unarmed_damage[0], entity.fighter.unarmed_damage[1]))
    libtcod.console_print_rect_ex(window, 0, 4, char_screen_width, char_screen_height,
        libtcod.BKGND_NONE, libtcod.LEFT, "AC: {}".format(entity.fighter.ac))

    x = screen_width - char_screen_width
    y = screen_height - char_screen_height

    libtcod.console_blit(window, 0, 0, char_screen_width, char_screen_height,
        0, x, y, 1.0, 0.7)