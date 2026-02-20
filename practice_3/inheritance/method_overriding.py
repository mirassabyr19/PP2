class Animal:
    def speak(self):
        print("Animal makes a sound")


class Dog(Animal):
    def speak(self):  # overriding
        print("Dog says: Woof!")


a = Animal()
d = Dog()

a.speak()  # Animal version
d.speak()  # Dog version