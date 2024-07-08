import pytest
import types
import sys, os, re
from functools import partial
from collections import Counter
from collections.abc import Iterable
from ..decorules.has_enforced_rules import HasEnforcedRules
from ..decorules.decorules_decs import raiseErrorIfFalseOnClass, raiseErrorIfFalseOnInstance

@pytest.fixture
def key_type_enforcer():
    def key_type_enforcer1(instance_object, enforced_type: type, enforced_key: str):
        member_object = getattr(instance_object, enforced_key, None)
        if member_object is None:
            return False
        return type(member_object) == enforced_type
    return key_type_enforcer1

@pytest.fixture
def min_value():
    def min_value1(instance_object, enforced_key: str, min_value):
        member_object = getattr(instance_object, enforced_key, None)
        if member_object is None:
            return False
        return member_object > min_value
    return min_value1

@pytest.fixture
def min_list_type_counter():
    def min_list_type_counter1(instance_object, list_name: str, min_counter: Counter):
        member_object = getattr(instance_object, list_name, None)
        if member_object is None:
            return False
        if isinstance(member_object, Iterable):
            return Counter(type(x) for x in member_object) >= min_counter
        else:
            return False
    return min_list_type_counter1


def test_class_method_OK_1(key_type_enforcer):
    try:    
        @raiseErrorIfFalseOnClass(partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def library_functionality(self):
                return 1
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")
    
def test_class_method_fails_1(key_type_enforcer):
    with pytest.raises(AttributeError):    
        @raiseErrorIfFalseOnClass(partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            pass

def test_class_method_OK_2(min_list_type_counter):
    geq_type_dict = {str: 1, int: 2, float:1}
    try:    
        @raiseErrorIfFalseOnClass(partial(min_list_type_counter, list_name='STATIC_LIST', min_counter = Counter({str: 1, int: 2, float:1})), AttributeError, f"STATIC_LIST member must have these or more {geq_type_dict}")
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            STATIC_LIST = ("Test", 10, 40, 50, 45.5, 60.0, '3', 'i', BaseException())
            pass
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")
    
def test_class_method_fails_2(min_list_type_counter):
    geq_type_dict = {str: 1, int: 2, float:1}
    with pytest.raises(AttributeError):    
        @raiseErrorIfFalseOnClass(partial(min_list_type_counter, list_name='STATIC_LIST', min_counter = Counter({str: 1, int: 2, float:1})), AttributeError, f"STATIC_LIST member must have these or more {geq_type_dict}")
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            STATIC_LIST = ("Test", 10, 40, 50, '3', 'i', BaseException())
            pass

def test_instance_method_OK_1(key_type_enforcer):
    try:    
        @raiseErrorIfFalseOnInstance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError) 
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.x = value
        a = NormalLibraryClass()                
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")
    except BaseException as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with Exception {type(ex)} {str(ex)}")

def test_instance_method_fails_1(key_type_enforcer):
    with pytest.raises(AttributeError):    
        @raiseErrorIfFalseOnInstance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError) 
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.y = value
        a = NormalLibraryClass()

def test_instance_method_fails_2(key_type_enforcer):
    with pytest.raises(AttributeError):    
        @raiseErrorIfFalseOnInstance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError) 
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.x = value
                del self.x
        a = NormalLibraryClass()
