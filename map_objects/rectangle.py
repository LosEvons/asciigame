class Rect:
    """
    A class to generate rectangles, that we then use to generate rooms.
    """
    def __init__ (self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self): #Finds the center of a rectangle
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return(center_x, center_y)

    def intersect(self, other): #Sees if the rectangle has overlap with any other rooms.
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)