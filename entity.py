import math
import tcod as libtcod
from components.item import Item
from render_functions import RenderOrder

class Entity:
    """
    A generic object to represent players, enemise, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False,
        render_order=RenderOrder.CORPSE, fighter=None, ai=None,
        item=None, inventory=None, stairs=None, level=None,
        equipment=None, equippable=None): #Entities do not block or have any ai-script by default
        
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter  #Defines class
        self.ai = ai #Defines ai script
        self.render_order = render_order #When is the entity rendered (so things don't disappear under each other so much)
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable

        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self
        if self.item:
            self.item.owner = self
        if self.inventory:
            self.inventory.owner = self
        if self.stairs:
            self.stairs.owner = self
        if self.level:
            self.level.owner = self
        if self.equipment:
            self.equipment.owner = self
        if self.equippable:
            self.equippable.owner = self
            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    def move(self, dx, dy): #Used to move stuff. Takes a change in coordinates.
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities): #Used to move stuff towards a point. 
        dx = target_x - self.x                                      #Calculates a very simple route to a point, and avoids blocking objects on it's way there.
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
            
        for entity in entities: #Makes other entities transparent to better pathfinding.
            if entity.blocks and entity != self and entity != target:
                fov.transparent[entity.y][entity.x] = True
                fov.walkable[y1][x1] = False

        my_path = libtcod.path_new_using_map(fov, 1.41) #Creates a new path. 1.41 affects how the algorithm sees the cost of diagonal and cardinal movement to be.

        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y) #More computation for the path.

        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25: #If path isn't empty and path isn't too long, allow movement.
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                self.x = x
                self.y = y
        else:
            self.move_towards(target.x, target.y, game_map, entities)

        libtcod.path_delete(my_path) #Deletes path currently. We just make a new path every time. Might be a source of performance issues down the line.
    
    def distance_to(self, other): #Pythagorean theorem. Calculates the lenght of the hypotenuse.
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def get_blocking_entities_at_location(self, entities, destination_x, destination_y): #Finds any entities at a location, and checks if they are supposed to block the player.
        for entity in entities:                                                    #Takes the predicted location of a moving entity.
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity       #Returns the entity we are colliding with

        return None