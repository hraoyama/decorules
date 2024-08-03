import sys
import operator
from library_class import LibraryClass, ProducerBaseClass
from decorules.decorators import (raise_if_false_on_class,
                                  raise_if_false_on_instance,
                                  run_if_false_on_instance,
                                  run_instance_rules,
                                  run_instance_actions)
from decorules.has_rules_actions import HasRulesActions
from decorules.utils import member_enforcer

smallest_coordinate_times_multiplier_larger_than_largest = lambda x: min(x.coordinates) * x.MULTIPLIER > max(
    x.coordinates)


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


@raise_if_false_on_instance(smallest_coordinate_times_multiplier_larger_than_largest,
                            ValueError,
                            "Checks that the multiplier times the smallest coordinate is larger than the largest "
                            "coordinate")
@raise_if_false_on_class(member_enforcer('MULTIPLIER', float, 1.0, operator.gt),
                         AttributeError,
                         "Checks that the multiplier is larger than 1.0")
class ClientClass(LibraryClass):
    MULTIPLIER = 2.5

    @run_instance_rules
    def append(self, value=0.0):
        self.coordinates.append(value)


class SomeBaseClass:
    def foo(self):
        print(f"Executing method {sys._getframe().f_code.co_name} of {self.__class__.__name__}")
        pass


class MultipleInheritanceClass(SomeBaseClass, ClientClass):
    @run_instance_rules
    def multiply_multiplier(self, value=1.0):
        self.MULTIPLIER = self.MULTIPLIER * value


class SomeOtherClass(SomeBaseClass):
    @run_instance_rules
    def foo(self):
        print(f"Executing method {sys._getframe().f_code.co_name} of {self.__class__.__name__}")
        pass


class LayerClass1(ClientClass):
    pass


class LayerClass2(LayerClass1):
    pass


class LayerClass3(LayerClass2):
    pass


class LayerClass4(LayerClass3):
    pass


@raise_if_false_on_instance(is_mean_entry_lt_30, ValueError, "Average number to process must be <30")
@raise_if_false_on_instance(is_last_entry_lt_50, ValueError, "Refuse to accept value >50")
class LargeNumberProcessor(metaclass=HasRulesActions):
    def __init__(self):
        self.to_process_list = []

    @run_instance_rules
    def append_number(self, value: int):
        self.to_process_list.append(value)

    @run_instance_rules
    def process_front_number(self):
        if self.to_process_list:
            return self.to_process_list.pop(0)
        else:
            return None

    def __len__(self):
        return len(self.to_process_list)

    def __getitem__(self, item: int):
        if self.to_process_list:
            return self.to_process_list[item]
        else:
            return None


NUMBER_PROCESSOR = LargeNumberProcessor()


def add_to_LNP(instance):
    NUMBER_PROCESSOR.append_number(instance.m)


@run_if_false_on_instance(is_m_lt_20, add_to_LNP)
@raise_if_false_on_instance(is_m_positive_and_lt_100, AttributeError)
class DerivedProducerClass(ProducerBaseClass):
    def __init__(self, value: int = 0):
        self.m = value

    @run_instance_actions
    @run_instance_rules
    def add(self, other: int):
        self.m += other


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
    d = ClientClass("d", 0.1, 0.1, 0.05)
    d.testme()
    try:
        e = ClientClass("e", 0.1, 0.1, 0.025)
        e.testme()
    except ValueError as ve:
        print(ve)
        pass
    try:
        f = ClientClass("f", 0.8, 0.8, 0.4)
        f.testme()
    except ValueError as ve:
        print(ve)
        pass
    g = ClientClass("g", 0.1, 0.1, 0.05)
    g.testme()
    g.append(0.06)  # should not break an instance rule
    g.testme()
    try:
        g.append(max(g.coordinates) * ClientClass.MULTIPLIER)  # should break
        g.testme()
    except ValueError as ve:
        print(ve)
        pass
    h = MultipleInheritanceClass("h", 0.1, 0.1, 0.05)
    h.multiply_multiplier(1.0)
    h.testme()
    h.multiply_multiplier(10.0)
    h.testme()
    try:
        h.multiply_multiplier(0.001)
        h.testme()
    except ValueError as ve:
        print(ve)
        pass
    i = SomeOtherClass()
    try:
        i.foo()
    except TypeError as te:
        print(te)
        pass

    j = LayerClass4("j", 0.1, 0.1, 0.05)
    j.append(0.06)  # should not break an instance rule#
    try:
        j.append(max(j.coordinates) * LayerClass4.MULTIPLIER)  # should break
    except ValueError as ve:
        print(ve)
        pass

    k = DerivedProducerClass()
    k.add(5)
    assert len(NUMBER_PROCESSOR) == 0
    k.add(5)
    assert len(NUMBER_PROCESSOR) == 0
    k.add(5)
    assert len(NUMBER_PROCESSOR) == 0
    k.add(5)
    assert len(NUMBER_PROCESSOR) == 1
    assert NUMBER_PROCESSOR[-1] == 20
    k.add(5)
    assert len(NUMBER_PROCESSOR) == 2
    assert NUMBER_PROCESSOR[-1] == 25
    k.add(-14)
    assert len(NUMBER_PROCESSOR) == 2
    assert NUMBER_PROCESSOR[-1] == 25
    k.add(11)
    assert len(NUMBER_PROCESSOR) == 3
    assert NUMBER_PROCESSOR[-1] == 22
    NUMBER_PROCESSOR.process_front_number()
    k.add(8)
    assert len(NUMBER_PROCESSOR) == 3
    assert NUMBER_PROCESSOR[-1] == 30
    assert NUMBER_PROCESSOR.to_process_list == [25, 22, 30]
    NUMBER_PROCESSOR.process_front_number()
    try:
        NUMBER_PROCESSOR.process_front_number()
    except ValueError as ve:
        print(ve)
        pass
    assert NUMBER_PROCESSOR.to_process_list == [30]
    k.add(-11)
    assert NUMBER_PROCESSOR.to_process_list == [30]
    try:
        k.add(29)
    except ValueError as ve:
        print(ve)
        pass
    assert NUMBER_PROCESSOR.to_process_list == [30, 48]
    try:
        k.add(10)
    except ValueError as ve:
        print(ve)
        pass


if __name__ == "__main__":
    main()
