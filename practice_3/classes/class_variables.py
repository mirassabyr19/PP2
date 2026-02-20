class Person:
    species = "Human"   # class variable

    def __init__(self, name):
        self.name = name
p1 = Person("Miras")
p2 = Person("Ali")

print(p1.species)  # Human
print(p2.species)  # Human