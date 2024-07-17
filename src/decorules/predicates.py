import sys, os, re


# this file is not necessary and should be provided by the user

def key_type_enforcer1(instance_object, enforced_type: type, enforced_key: str):
    member_object = getattr(instance_object, enforced_key, None)
    if member_object is None:
        return False
    return type(member_object) == enforced_type
