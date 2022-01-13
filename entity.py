import math

import tcod as libtcod

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

    def move_astar(self, target, entities, game_map):
        fov = libtcod.map_new(game_map.width, game_map.height) #A new fov map used by a more robust pathfinding algorithm - https://en.wikipedia.org/wiki/A*_search_algorithm
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                fov.transparent[y1][x1] = not game_map.tiles[x1][y1].block_sight
                fov.walkable[y1][x1] = not game_map.tiles[x1][y1].blocked
            
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                fov.transparent[entity.y][entity.x] = True
                fov.walkable[y1][x1] = False

        my_path = libtcod.path_new_using_map(fov, 1.41) #Creates a new path. 1.41 affects how the algorithm sees the cost of diagonal and cardinal movement to be.

        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                self.x = x
                self.y = y
        else:
            self.move_towards(target.x, target.y, game_map, entities)

        libtcod.path_delete(my_path)
    
    def distance_to(self, other): 
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_blocking_entities_at_location(self, entities, destination_x, destination_y): #Finds any entities at a location, and checks if they are supposed to block the player.
        for entity in entities:                                                    #Takes the predicted location of a moving entity.
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity       #Returns the entity we are colliding with

        return None