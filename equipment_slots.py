from enum import Enum

class EquipmentSlots(Enum):
    MAIN_HAND = 1
    OFF_HAND = 2
    HEAD = 3
    SHOULDERS = 4
    CHEST = 5
    ARMS = 6
    RIGHT_HAND = 7
    LEFT_HAND = 8
    WAIST = 9
    LEGS = 10
    FEET = 11

class Bodyparts:
    parts = {
        "main_hand":None,
        "off_hand":None,
        "head":None,
        "shoulders":None,
        "chest":None,
        "arms":None,
        "right_hand":None,
        "left_hand":None,
        "waist":None,
        "legs":None,
        "feet":None
    }