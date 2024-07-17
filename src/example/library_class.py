import types
from functools import partial
from decorules.has_enforced_rules import HasEnforcedRules
from decorules.decorators import raise_if_false_on_class, raise_if_false_on_instance
from decorules.predicates import key_type_enforcer
from collections.abc import Iterable


def key_structure_enforcer(input_type,
                      enforced_type: type,
                      enforced_key: str):
    member_object = getattr(input_type, enforced_key, None)
    if member_object is None:
        return False
    else:
        return issubclass(type(member_object), enforced_type)
    pass


has_static_multiplier = partial(key_type_enforcer, enforced_type=float, enforced_key='MULTIPLIER', attrs=None)
has_testme_method = partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='testme', attrs=None)
are_coordinates_set_after_init = partial(key_type_enforcer, enforced_type=Iterable, enforced_key='coordinates')
are_coordinates_within_distance_1 = lambda y: (sum([x ** 2 for x in y.coordinates]) ** 0.5)<=1.0
has_second_static_multiplier = partial(key_structure_enforcer, enforced_type=float, enforced_key='NOT_USED_MULTIPLIER')

@raise_if_false_on_instance(are_coordinates_within_distance_1, ValueError, 'initial coordinates are outside the unit circle (euclidean distance)')
@raise_if_false_on_instance(are_coordinates_set_after_init, AttributeError, 'Missing coordinates after initialization')
@raise_if_false_on_class(has_testme_method, AttributeError, "Checks if a method called testme is present")
@raise_if_false_on_class(has_static_multiplier, AttributeError, "Checks if a float multiplier is set on the class")
class LibraryClass(metaclass=HasEnforcedRules):
    MULTIPLIER = 0.5
    NOT_USED_MULTIPLIER = 20.0
    def __init__(self, name : str, *args):
        self.name = name
        self.coordinates = list(args)
    def testme(self):
        print(self.name)
    pass






