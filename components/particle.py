import math

class Particle:
    def __init__(self, x, y, color, char, origin, destination):
        self.x = x
        self.y = y
        self.color = color
        self.char = char
        self.origin = origin
        self.destination = destination
        self.destroyed = False
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, game_map):
        if not self.destroyed:
            dx = self.destination - self.x
            dy = self.destination - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            dx = int(round(dx / distance))
            dy = int(round(dy / distance))

            if not (game_map.is_blocked(self.x + dx, self.y + dy):
                self.move(dx, dy)
        
        else:
            self.destroyed = True