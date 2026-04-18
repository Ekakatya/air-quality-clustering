import turtle

class Polygon:
    def __init__(self, sides, name, size=100, color = 'black', line_thickness = 2): # everything after self is what we need to mention
        self.sides = sides
        self.name = name
        self.size = size
        self.color = color
        self.line_thickness = line_thickness
        self.interior_angles = (self.sides - 2)*180
        self.angle = self.interior_angles / self.sides

    def draw(self):
        turtle.color(self.color)
        turtle.pensize(self.line_thickness)
        for i in range(self.sides):
            turtle.forward(self.size)
            turtle.right(180 - self.angle)
        turtle.done()


class Square(Polygon):
    def __init__(self, size=100, color = 'black', line_thickness = 2):
        super().__init__(4, 'Square', size, color, line_thickness)

    def draw(self):
        turtle.begin_fill()
        super().draw()
        turtle.end_fill()




square = Square(color='#123abc', line_thickness = 12)

print(square.sides)
print(square.name)
print(square.angle)

print(square.draw())

turtle.done()

# square = Polygon(4, 'Square')
# pentagon = Polygon(5, 'Pentagon')
# hexagon = Polygon(6, 'Hexagon', 150, 'red', 20)
#
# print(square.sides)
# print(square.name)
# print(square.interior_angles)
# print(square.ange)
#
# print(pentagon.sides)
# print(pentagon.name)
#
# hexagon.draw()
