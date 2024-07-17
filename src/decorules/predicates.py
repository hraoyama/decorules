import sys, os, re
from collections import Counter
from collections.abc import Iterable


# this file is in theory not necessary and should be provided by the user
# but we provide some examples here that are used in the tests
# For the tests, do not put these in a fixture, because they get set in a class level container and key

def key_type_enforcer(instance_or_type,
                      enforced_type: type,
                      enforced_key: str,
                      attrs: dict = None):
    member_object = getattr(instance_or_type, enforced_key, None)
    if member_object is None:
        if attrs is not None:
            member_object = attrs.get(enforced_key, None)
    if member_object is None:
        return False
    else:
        return issubclass(type(member_object), enforced_type)
    pass


def min_value(instance_or_type,
              enforced_key: str,
              hard_floor):
    member_object = getattr(instance_or_type, enforced_key, None)
    if member_object is None:
        return False
    return member_object > hard_floor

def min_list_type_counter(instance_or_type,
                          list_name: str,
                          min_counter: Counter,
                          attrs: dict = None):
    member_object = getattr(instance_or_type, list_name, None)
    if member_object is None:
        if attrs is not None:
            member_object = attrs.get(list_name, None)
    if member_object is None:
        return False
    else:
        if isinstance(member_object, Iterable):
            return Counter(type(x) for x in member_object) >= min_counter
        else:
            return False
