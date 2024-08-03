import pytest
import types
import sys
import operator
from functools import partial
from collections import Counter
from dataclasses import dataclass, field
from decorules.has_rules_actions import HasRulesActions
from decorules.decorators import (raise_if_false_on_class,
                                  raise_if_false_on_instance,
                                  run_if_false_on_instance,
                                  run_instance_rules,
                                  run_instance_actions
                                  )
from decorules.predicates import key_type_enforcer, min_value, min_list_type_counter
from decorules.utils import member_enforcer


def test_class_type_wrong_fails_1():
    with pytest.raises(TypeError):
        check_method_present = partial(key_type_enforcer,
                                       enforced_type=types.FunctionType,
                                       enforced_key='foo')

        @raise_if_false_on_class(check_method_present, AttributeError, 'Checks if foo method exists')
        class NotRightTypeClass:
            def foo(self):
                print(f"Executing method {sys._getframe().f_code.co_name}")


def test_class_method_ok_1():
    check_method_present = partial(key_type_enforcer,
                                   enforced_type=types.FunctionType,
                                   enforced_key='library_functionality')
    try:
        @raise_if_false_on_class(check_method_present, AttributeError)
        class HasCorrectMethodClass(metaclass=HasRulesActions):
            def library_functionality(self):
                return 1
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")


def test_class_method_fails_1():
    with pytest.raises(AttributeError):
        check_method_present = partial(key_type_enforcer,
                                       enforced_type=types.FunctionType,
                                       enforced_key='library_functionality')

        @raise_if_false_on_class(check_method_present, AttributeError)
        class MissingCorrectMethodClass(metaclass=HasRulesActions):
            pass


def test_class_attribute_ok_2():
    geq_type_dict = {str: 1, int: 2, float: 1}
    static_member_name = "STATIC_SET"
    check_has_enough_of_type = partial(min_list_type_counter,
                                       list_name=static_member_name,
                                       min_counter=Counter(geq_type_dict))
    try:
        @raise_if_false_on_class(check_has_enough_of_type,
                                 AttributeError,
                                 f"f{static_member_name} must have these or more {geq_type_dict}")
        class HasSufficientStaticSetClass(metaclass=HasRulesActions):
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
        class HasInsufficientStaticSetClass(metaclass=HasRulesActions):
            STATIC_LIST = ("Test", 10, 40, 50, '3', 'i', BaseException())
            pass


def test_instance_method_ok_1():
    try:
        @raise_if_false_on_instance(partial(key_type_enforcer,
                                            enforced_type=int,
                                            enforced_key='x'),
                                    AttributeError)
        class HasCorrectInstanceMemberVariable(metaclass=HasRulesActions):
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
        class HasIncorrectInstanceMemberVariable(metaclass=HasRulesActions):
            def __init__(self, value=20):
                self.y = value

        a = HasIncorrectInstanceMemberVariable()


def test_instance_method_fails_2():
    with pytest.raises(AttributeError):
        @raise_if_false_on_instance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError)
        class HasDeletedInstanceMemberVariable(metaclass=HasRulesActions):
            def __init__(self, value=20):
                self.x = value
                del self.x

        a = HasDeletedInstanceMemberVariable()


def test_instance_on_method_ok_1():
    @raise_if_false_on_instance(partial(key_type_enforcer,
                                        enforced_type=int,
                                        enforced_key='y'), AttributeError)
    @raise_if_false_on_instance(lambda x: x.y < 10, ValueError)
    class HasMethodCheckedOKAfterCall(metaclass=HasRulesActions):
        def __init__(self, value=20):
            self.y = value

        @run_instance_rules
        def add(self, value=0):
            self.y += value

    a = HasMethodCheckedOKAfterCall(0)
    a.add(1)
    a.add(1)
    a.add(1)


def test_instance_on_method_fails_1():
    @raise_if_false_on_instance(partial(key_type_enforcer,
                                        enforced_type=int,
                                        enforced_key='y'), AttributeError)
    @raise_if_false_on_instance(lambda x: x.y < 10, ValueError)
    class HasMethodCheckedAndFailsAfterCall(metaclass=HasRulesActions):
        def __init__(self, value=20):
            self.y = value

        @run_instance_rules
        def add(self, value=0):
            self.y += value

    a = HasMethodCheckedAndFailsAfterCall(0)
    a.add(1)
    a.add(1)
    a.add(1)
    with pytest.raises(ValueError):
        a.add(10)


def test_instance_on_method_ok_2():
    @raise_if_false_on_instance(partial(key_type_enforcer,
                                        enforced_type=int,
                                        enforced_key='y'), AttributeError)
    @raise_if_false_on_instance(lambda x: x.y < 10, ValueError)
    class HasMethodCheckedOKAfterCall2(metaclass=HasRulesActions):
        def __init__(self, value=20):
            self.y = value

        @run_instance_rules
        def add(self, value=0):
            self.y += value

    a = HasMethodCheckedOKAfterCall2(0)
    a.add(1)
    a.add(1)
    a.add(1)
    a.add(1)
    a.add(-10)
    a.add(1)
    a.add(10)


def test_class_type_wrong_fails_using_util_1():
    with pytest.raises(TypeError):
        @raise_if_false_on_class(member_enforcer(enforced_type=types.FunctionType, enforced_key='foo'),
                                 AttributeError,
                                 'Checks if foo method exists')
        class NotRightTypeUsingUtilClass:
            def foo(self):
                print(f"Executing method {sys._getframe().f_code.co_name}")


def test_class_method_ok_using_util_1():
    try:
        @raise_if_false_on_class(member_enforcer('library_functionality', types.FunctionType), AttributeError)
        class HasCorrectMethodUsingUtilClass(metaclass=HasRulesActions):
            def library_functionality(self):
                return 1
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")


def test_class_method_ok_using_util_2():
    try:
        @raise_if_false_on_class(member_enforcer('static_member', int, 20), AttributeError)
        class HasStaticUsingDecClass(metaclass=HasRulesActions):
            static_member = 20
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")


def test_class_method_ok_using_util_3():
    try:
        @raise_if_false_on_class(member_enforcer('static_member', int, 20, operator.gt), AttributeError)
        class HasLargeEnoughStaticUsingDecClass(metaclass=HasRulesActions):
            static_member = 25
    except AttributeError as ex:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with AttributeError {str(ex)}")


def test_class_method_fails_using_util_1():
    with pytest.raises(AttributeError):
        @raise_if_false_on_class(
            member_enforcer(enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
        class MissingCorrectMethodUsingDecClass(metaclass=HasRulesActions):
            pass


def test_class_method_fails_using_util_2():
    with pytest.raises(AttributeError):
        @raise_if_false_on_class(member_enforcer('static_member', int, 20, operator.lt), AttributeError)
        class HasTooLargeStaticUsingDecClass(metaclass=HasRulesActions):
            static_member = 25


def test_instance_runs_action_ok_1():
    storage_list = []

    def add_to_list(input_list, instance):
        input_list.append(instance._m)

    add_to_storage_list = partial(add_to_list, storage_list)
    is_m_lt_10 = lambda x: x._m < 10

    @run_if_false_on_instance(is_m_lt_10, add_to_storage_list)
    @dataclass
    class StoresNumeric(metaclass=HasRulesActions):
        _m: int = field(default=0)

        @property
        def m(self):
            return self._m

        # order of the decorators is important here!
        @m.setter
        @run_instance_actions
        def m(self, new_value):
            self._m = new_value

    a = StoresNumeric(9)
    if storage_list:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    a.m = 5
    if storage_list:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    a.m = 10
    if not storage_list:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    a.m = 12
    if not len(storage_list) > 1:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    if storage_list[-1] != 12:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    a.m = 11
    if not len(storage_list) > 2:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    if storage_list[-1] != 11:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    a.m = 10
    if not len(storage_list) > 3:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    if storage_list[-1] != 10:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    a.m = 4
    if len(storage_list) != 4:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")
    if storage_list[-1] != storage_list[0]:
        pytest.fail(f"Failed {sys._getframe().f_code.co_name} with storage_list {storage_list}")


def test_instance_runs_and_raises_ok_1():
    def is_m_positive_and_lt_100(instance):
        return (instance.m >= 0) & (instance.m < 100)

    def is_m_lt_20(instance):
        return instance.m < 20

    def is_last_entry_lt_50(instance):
        if instance.to_process_list:
            return instance.to_process_list[-1] < 50
        else:
            return True  # still empty list

    def is_mean_entry_lt_30(instance):
        if instance.to_process_list:
            return sum(instance.to_process_list) / len(instance.to_process_list) < 30.0
        else:
            return True  # still empty list

    def halve_list(instance):
        if instance.to_process_list:
            instance.to_process_list = [int(x*0.5) for x in instance.to_process_list]

    @run_if_false_on_instance(is_mean_entry_lt_30, halve_list)
    @raise_if_false_on_instance(is_last_entry_lt_50, ValueError, "Refuse to accept value >50")
    class LargeNumberProcessor(metaclass=HasRulesActions):
        def __init__(self):
            self.to_process_list = []

        @run_instance_actions
        @run_instance_rules
        def append_number(self, value: int):
            self.to_process_list.append(value)

        @run_instance_actions
        @run_instance_rules
        def process_front_number(self):
            if self.to_process_list:
                return self.to_process_list.pop(0)
            else:
                return None

    NUMBER_PROCESSOR = LargeNumberProcessor()

    def add_to_LNP(instance):
        NUMBER_PROCESSOR.append_number(instance.m)

    @run_if_false_on_instance(is_m_lt_20, add_to_LNP)
    @raise_if_false_on_instance(is_m_positive_and_lt_100, AttributeError)
    class ProducerClass(metaclass=HasRulesActions):
        def __init__(self, value: int = 0):
            self.m = value

        @run_instance_actions
        @run_instance_rules
        def add(self, other: int):
            self.m += other

    k = ProducerClass()
    k.add(5)
    k.add(5)
    k.add(5)
    assert len(NUMBER_PROCESSOR.to_process_list) == 0
    k.add(5)
    assert len(NUMBER_PROCESSOR.to_process_list) == 1  # first value of 20 is sent
    k.add(5)
    assert NUMBER_PROCESSOR.to_process_list[-1] == 25  
    k.add(-14)
    assert NUMBER_PROCESSOR.to_process_list[-1] == 25 # we dropped below 20 so no new value was passed
    k.add(11)
    NUMBER_PROCESSOR.process_front_number() # 20 is gone from the list
    k.add(8)
    assert NUMBER_PROCESSOR.to_process_list == [25, 22, 30]
    NUMBER_PROCESSOR.process_front_number()
    assert NUMBER_PROCESSOR.to_process_list == [22, 30]
    NUMBER_PROCESSOR.process_front_number()  # because the list average is now [30], its values will get halved
    assert NUMBER_PROCESSOR.to_process_list == [15]
    k.add(-9) # the managed int goes from 30 to 21
    assert NUMBER_PROCESSOR.to_process_list == [15, 21]
    with(pytest.raises(ValueError)):
        k.add(40)  # will raise a ValueError as we try to pass 61 to the LargeNumberProcessor



