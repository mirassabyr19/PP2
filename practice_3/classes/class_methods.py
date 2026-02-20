class Person:
  def __init__(self, name):
    self.name = name

  def greet(self):                              #methods are functions that belongs to the class
    print("Hello, my name is " + self.name)

p1 = Person("Emil")
p1.greet()
