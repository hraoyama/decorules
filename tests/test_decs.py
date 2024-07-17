import pytest
import types
import sys
from functools import partial
from collections import Counter
from collections.abc import Iterable
# make sure to add to python path!
from has_enforced_rules import HasEnforcedRules
from decorators import raise_if_false_on_class, raise_if_false_on_instance


@pytest.fixture
def key_type_enforcer():
    def key_type_enforcer1(instance_object, enforced_type: type, enforced_key: str, attrs : dict = None):
        member_object = getattr(instance_object, enforced_key, None)
        if member_object is None:
            if attrs is not None:
                member_object = attrs.get(enforced_key, None)
        if member_object is None:
            return False
        else:
            return issubclass(type(member_object), enforced_type)
        pass
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
    def min_list_type_counter1(instance_object, list_name: str, min_counter: Counter, attrs : dict = None):
        member_object = getattr(instance_object, list_name, None)
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

    return min_list_type_counter1


@pytest.mark.skip
def test_class_method_ok_1(key_type_enforcer):
    try:
        @raise_if_false_on_class(partial(key_type_enforcer,
                                         enforced_type=types.FunctionType,
                                         enforced_key='library_functionality'),
                                 AttributeError)
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def library_functionality(self):
                return 1
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")

@pytest.mark.skip
def test_class_method_fails_1(key_type_enforcer):
    # with pytest.raises(AttributeError):
    try:
        @raise_if_false_on_class(partial(key_type_enforcer,
                                         enforced_type=types.FunctionType,
                                         enforced_key='library_functionality'),
                                 AttributeError)
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            pass
    except AttributeError as ex:
        pass
    else:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} should have raised AttributeError but did not")


@pytest.mark.skip
def test_class_method_ok_2(min_list_type_counter):
    geq_type_dict = {str: 1, int: 2, float: 1}
    try:
        @raise_if_false_on_class(partial(min_list_type_counter,
                                         list_name='STATIC_LIST',
                                         min_counter=Counter({str: 1, int: 2, float: 1})),
                                 AttributeError,
                                 f"STATIC_LIST member must have these or more {geq_type_dict}")
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            STATIC_LIST = ("Test", 10, 40, 50, 45.5, 60.0, '3', 'i', BaseException())
            pass
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")


def test_class_method_fails_2(min_list_type_counter):
    geq_type_dict = {str: 1, int: 2, float: 1}
    with pytest.raises(AttributeError):
        @raise_if_false_on_class(partial(min_list_type_counter,
                                         list_name='STATIC_LIST',
                                         min_counter=Counter({str: 1, int: 2, float: 1})),
                                 AttributeError,
                                 f"STATIC_LIST member must have these or more {geq_type_dict}")
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            STATIC_LIST = ("Test", 10, 40, 50, '3', 'i', BaseException())
            pass


def test_instance_method_ok_1(key_type_enforcer):
    try:
        @raise_if_false_on_instance(partial(key_type_enforcer,
                                            enforced_type=int,
                                            enforced_key='x'),
                                    AttributeError)
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
        @raise_if_false_on_instance(partial(key_type_enforcer,
                                            enforced_type=int,
                                            enforced_key='x'),
                                    AttributeError)
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.y = value

        a = NormalLibraryClass()


@pytest.mark.skip
def test_instance_method_fails_2(key_type_enforcer):
    with pytest.raises(AttributeError):
        @raise_if_false_on_instance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError)
        class NormalLibraryClass(metaclass=HasEnforcedRules):
            def __init__(self, value=20):
                self.x = value
                del self.x

        a = NormalLibraryClass()
