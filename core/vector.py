class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_list(self):
        return self.x, self.y

    def minus(self, vec):
        return Vector(self.x - vec.x, self.y - vec.y)
