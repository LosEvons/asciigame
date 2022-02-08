class Rect:
    """
    A class to generate rectangles, that we then use to generate rooms.
    """
    def __init__ (self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.tl_corner = (self.x1, self.y1)
        self.tr_corner = (self.x2-1, self.y1)
        self.bl_corner = (self.x1, self.y2-1)
        self.br_corner = (self.x2-1, self.y2-1)

    def center(self): #Finds the center of a rectangle
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return(center_x, center_y)

    def intersect(self, other): #Sees if the rectangle has overlap with any other rooms.
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    @property
    def edge(self):
        top = [(x, y) for x in range(self.x1, self.x2) for y in range(self.y1, self.y2) if y == self.y1]
        bottom = [(x, y) for x in range(self.x1, self.x2) for y in range(self.y1, self.y2) if y == self.y2-1]
        left = [(x, y) for x in range(self.x1, self.x2) if x == self.x1 for y in range(self.y1, self.y2)]
        right = [(x, y) for x in range(self.x1, self.x2) if x == self.x2-1 for y in range(self.y1, self.y2)]



        return top, bottom, left, right

    def get_shared_tiles(self, other):
        shared_tiles = []

        own_tiles = self.edge
        other_tiles = other.edge

        for side in own_tiles:
            for tile in side:
                if tile in (tile2 for side2 in other_tiles for tile2 in side2):
                    shared_tiles.append(tile)
                
        return shared_tiles