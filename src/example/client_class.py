import types
from library_class import LibraryClass
from decorules.decorators import raise_if_false_on_class, raise_if_false_on_instance, enforces_instance_rules

is_multiplier_larger_than_1 = lambda x: x.MULTIPLIER>1.0
smallest_coordinate_times_multiplier_larger_than_largest = lambda x: min(x.coordinates)*x.MULTIPLIER>max(x.coordinates)
@raise_if_false_on_instance(smallest_coordinate_times_multiplier_larger_than_largest,
                            ValueError,
                            "Checks that the multiplier times the smallest coordinate is larger than the largest coordinate")
@raise_if_false_on_class(is_multiplier_larger_than_1,
                         AttributeError,
                         "Checks that the multiplier is larger than 2.0")
class ClientClass(LibraryClass):
    MULTIPLIER = 2.5
    @enforces_instance_rules
    def append(self, value=0.0):
        self.coordinates.append(value)
    pass

def main():
    a = LibraryClass("a")
    a.testme()
    b = LibraryClass("b", 0.2, 0.5)
    b.testme()
    try:
        c = LibraryClass("c", -2.0, 0.5)
        c.testme()
    except ValueError as ve:
        print(ve)
        pass
    d = ClientClass("d", 0.1,0.1,0.05)
    d.testme()
    try:
        e = ClientClass("e",0.1,0.1,0.025)
        e.testme()
    except ValueError as ve:
        print(ve)
        pass
    try:
        f = ClientClass("f",0.8,0.8,0.4)
        f.testme()
    except ValueError as ve:
        print(ve)
        pass
    g = ClientClass("g", 0.1,0.1,0.05)
    g.testme()
    g.append(0.06)  # should not break an instance rule
    g.testme()
    try:
        g.append(max(g.coordinates)*ClientClass.MULTIPLIER) # should break
    except ValueError as ve:
        print(ve)
        pass


if __name__ == "__main__":
    main()

