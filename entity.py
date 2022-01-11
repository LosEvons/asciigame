from os import name


class Entity:
    """
    A generic object to represent players, enemise, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False): #Entities do not block by default
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

    def move(self, dx, dy): #Used to move stuff. Takes a change in coordinates.
        self.x += dx
        self.y += dy

    def get_blocking_entities_at_location(entities, destination_x, destination_y): #Finds any entities at a location, and checks if they are supposed to block the player.
        for entity in entities:                                                    #Takes the predicted location of a moving entity.
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity       #Returns the entity we are colliding with

        return None