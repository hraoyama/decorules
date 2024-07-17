import pytest
import types
import sys
from functools import partial
from collections import Counter
from collections.abc import Iterable
# make sure to add to python path!
from has_enforced_rules import HasEnforcedRules
from decorators import raise_if_false_on_class, raise_if_false_on_instance
from predicates import key_type_enforcer, min_value, min_list_type_counter

def test_class_method_ok_1():
    check_method_present = partial(key_type_enforcer,
                                   enforced_type=types.FunctionType,
                                   enforced_key='library_functionality')
    try:
        @raise_if_false_on_class(check_method_present, AttributeError)
        class HasCorrectMethodClass(metaclass=HasEnforcedRules):
            def library_functionality(self):
                return 1
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")


def test_class_method_fails_1():
    # with pytest.raises(AttributeError):
    check_method_present = partial(key_type_enforcer,
                                   enforced_type=types.FunctionType,
                                   enforced_key='library_functionality')
    try:
        @raise_if_false_on_class(check_method_present, AttributeError)
        class MissingCorrectMethodClass(metaclass=HasEnforcedRules):
            pass
    except AttributeError as ex:
        pass
    else:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} should have raised AttributeError but did not")

def test_class_attribute_ok_2():
    geq_type_dict = {str: 1, int: 2, float: 1}
    static_member_name = "STATIC_SET"
    check_has_enough_of_type = partial( min_list_type_counter,
                                        list_name=static_member_name,
                                        min_counter=Counter(geq_type_dict))
    try:
        @raise_if_false_on_class(check_has_enough_of_type,
                                 AttributeError,
                                 f"f{static_member_name} must have these or more {geq_type_dict}")
        class HasSufficientStaticSetClass(metaclass=HasEnforcedRules):
            STATIC_SET = ("Test", 10, 40, 50, 45.5, 60.0, '3', 'i', BaseException())
            pass
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")

def test_class_method_fails_2():
    geq_type_dict = {str: 1, int: 2, float: 1}
    with pytest.raises(AttributeError):
        @raise_if_false_on_class(partial(min_list_type_counter,
                                         list_name='STATIC_LIST',
                                         min_counter=Counter({str: 1, int: 2, float: 1})),
                                 AttributeError,
                                 f"STATIC_LIST member must have these or more {geq_type_dict}")
        class HasInsufficientStaticSetClass(metaclass=HasEnforcedRules):
            STATIC_LIST = ("Test", 10, 40, 50, '3', 'i', BaseException())
            pass


def test_instance_method_ok_1():
    try:
        @raise_if_false_on_instance(partial(key_type_enforcer,
                                            enforced_type=int,
                                            enforced_key='x'),
                                    AttributeError)
        class HasCorrectInstanceMemberVariable(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.x = value

        a = HasCorrectInstanceMemberVariable()
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")
    except BaseException as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with Exception {type(ex)} {str(ex)}")


def test_instance_method_fails_1():
    with pytest.raises(AttributeError):
        @raise_if_false_on_instance(partial(key_type_enforcer,
                                            enforced_type=int,
                                            enforced_key='x'),
                                    AttributeError)
        class HasIncorrectInstanceMemberVariable(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.y = value

        a = HasIncorrectInstanceMemberVariable()


def test_instance_method_fails_2():
    with pytest.raises(AttributeError):
        @raise_if_false_on_instance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError)
        class HasDeletedInstanceMemberVariable(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.x = value
                del self.x

        a = HasDeletedInstanceMemberVariable()
