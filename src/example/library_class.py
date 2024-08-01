import types
from functools import partial
from decorules.has_enforced_rules import HasEnforcedRules
from decorules.decorators import raise_if_false_on_class, raise_if_false_on_instance
from decorules.predicates import key_type_enforcer
from decorules.utils import member_enforcer
from collections.abc import Iterable

are_coordinates_within_distance_1 = lambda y: (sum([x ** 2 for x in y.coordinates]) ** 0.5) <= 1.0


@raise_if_false_on_instance(are_coordinates_within_distance_1, ValueError,
                            'initial coordinates are outside the unit circle (euclidean distance)')
@raise_if_false_on_instance(member_enforcer('coordinates', Iterable), AttributeError,
                            'Missing coordinates after initialization')
@raise_if_false_on_class(member_enforcer('testme', types.FunctionType), AttributeError,
                         "Checks if a method called testme is present")
@raise_if_false_on_class(member_enforcer('MULTIPLIER', float), AttributeError,
                         "Checks if a float multiplier is set on the class")
class LibraryClass(metaclass=HasEnforcedRules):
    MULTIPLIER = 0.5
    NOT_USED_MULTIPLIER = 20.0

    def __init__(self, name: str, *args):
        self.name = name
        self.coordinates = list(args)

    def testme(self):
        print(self.name)

    pass
