class Person:
  def __init__(self, name, age):    #use the __init__() method to assign values for name and age:
    self.name = name
    self.age = age

p1 = Person("Emil", 36)

print(p1.name)
print(p1.age)
