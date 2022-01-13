import math

class Entity:
    """
    A generic object to represent players, enemise, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False,
        fighter=None, ai=None): #Entities do not block or have any ai-script by default
        
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai
          
        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self

    def move(self, dx, dy): #Used to move stuff. Takes a change in coordinates.
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
            self.get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def distance_to(self, other): 
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_blocking_entities_at_location(self, entities, destination_x, destination_y): #Finds any entities at a location, and checks if they are supposed to block the player.
        for entity in entities:                                                    #Takes the predicted location of a moving entity.
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity       #Returns the entity we are colliding with

        return None