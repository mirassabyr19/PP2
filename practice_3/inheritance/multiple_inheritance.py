class Flyable:
    def fly(self):
        print("I can fly")


class Swimmable:
    def swim(self):
        print("I can swim")


class Duck(Flyable, Swimmable):
    def quack(self):
        print("Quack!")


d = Duck()

d.fly()
d.swim()
d.quack()