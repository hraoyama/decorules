# decorules

## Introduction

_decorules_ is a tiny python decorator library with two objectives:

A. To __enforce rules on class structure and instance behavior for classes and class hierarchies__ through decorators at the point of class declaration. Useful for library developers.

B. To __automatically trigger functionality using boolean conditions__ on an instance of a class[^1]  

The decorators employed are:

1. `raise_if_false_on_class` will raise an exception should class structure and/or attributes not adhere to user defined rules 
2. `raise_if_false_on_instance` will raise an exception should class instances not adhere to user defined rules[^2]
3. `run_if_false_on_instance` will run user supplied functionality should class instances not adhere to user defined criteria[^2]
4. `run_instance_rules` will apply the rules from 2. on any member function using this decorator 
5. `run_instance_actions` will apply the actions from 3. on any member function using this decorator

All rules and actions are specified through the __decorators on the class declaration__ and using the metaclass __HasRulesActions__ from the library. 

Enforcement of the rules is done by throwing exceptions (which can be developer specified) when a predicate function fails. 

The actions taken when a predicate fails are supplied by the user through functions taking the instance as argument. 


## Installation

_decorules_ was built using python `3.10`. It is available as a [package on pypi](https://pypi.org/project/decorules/) and can be installed through pip:

```
pip install decorules
```
Should you require an installation of pip, follow the instructions on the [pip website](https://pip.pypa.io/en/stable/installation/).

## Examples

A worked out example of several types of class hierarchies can be found under `src/example`, with `library_class.py` and `client_class.py` representing the library and client respectively.

Further examples, including interaction with other decorators[^3], can be found in the source file under the `tests` directory. 

The aim here is to simply walk through some simple examples to demonstrate usage. 

Firstly, suppose we wish to enforce that a (base) class or an instance of the class must have an attribute of a certain type. Here are the basic steps:

  1. Create a function that takes a class or an instance and checks whether an attribute exists and is of the correct type. In the example, this function is `key_type_enforcer`
```python
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
```
In order to guarantee that the class (and its derived classes) implements a function named `library_functionality` we would implement:

```python
from decorules.has_rules_actions import HasRulesActions
import types
from functools import partial

@raise_if_false_on_class(partial(key_type_enforcer, 
                                 enforced_type=types.FunctionType, 
                                 enforced_key='library_functionality'), 
                         AttributeError)
class HasCorrectMethodClass(metaclass=HasRulesActions):
    def library_functionality(self):
        return 1
```

2. For restrictions on instances, the function must be [predicate](https://stackoverflow.com/questions/1344015/what-is-a-predicate). This means the function takes one argument (the instance) and returns a boolean. Functions can be turned into predicates using different methods, in this example we will use `partial` from the `functools` package. For restrictions on classes that do not check the values of attributes predicate functions can be provided. If the rule on the class does make use of such a value (e.g., check if a static float is positive), the function must take 2 arguments and return a boolean. The second argument should always default to `None`[^4].  
3. Use the decorator `raise_if_false_on_class` when enforcing a rule on a class level, or `raise_if_false_on_instance` when enforcing upon instantiation. Both decorators take 1 compulsory argument (the function from step 2. which returns a True/False value) and 2 optional arguments, the first is the type of the exception to be raised should the rule not hold[^5] and the second optional argument is a string providing extra information when the exception is raised.
4. The rules on instances are only applied after the call to `__init__`. We have the option to add the `run_instance_rules` decorator to any method of the class, thereby enforcing the instance rules after each method call.

If in addition, we ensure that an `int` member named `x` existed after every instantiation:

```python
@raise_if_false_on_instance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError)  
@raise_if_false_on_class(partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class HasCorrectMethodAndInstanceVarClass(metaclass=HasRulesActions):
    def __init__(self, value=20):
        self.x = value
    def library_functionality(self):
        return 1
```

Should the `__init__` implementation not set `self.x` or remove it using `del self.x`, all of the following calls would throw an `AttributeError`:
```python
a = HasCorrectMethodAndInstanceVarClass()
b = HasCorrectMethodAndInstanceVarClass(25)
c = HasCorrectMethodAndInstanceVarClass(5)
```
For forcing the member `x` to be larger than 10:
```python
@raise_if_false_on_instance(lambda ins: ins.x > 10, ValueError, "Check x-member>10")  
@raise_if_false_on_instance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError)  
@raise_if_false_on_class(partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class HasCorrectMethodAndInstanceVarCheckClass(metaclass=HasRulesActions):
    def __init__(self, value=20):
        self.x = value
    def library_functionality(self):
        return 1
```
Note the third argument in the decorator, this will be prepended to the message of the exception. 
For the implementation above, only the third line would raise an exception:

```python
a = HasCorrectMethodAndInstanceVarCheckClass()
b = HasCorrectMethodAndInstanceVarCheckClass(25)
c = HasCorrectMethodAndInstanceVarCheckClass(5) # a ValueError is raised
```
Because the key-type + comparison paradigm is expected to be widely used for classes and instances, _decorules_ provides a utility for this called `member_enforcer`[^6]. The previous snippet could have been simplified using:

```python
import operator
from decorules.utils import member_enforcer

@raise_if_false_on_instance(member_enforcer('x',int, 10, operator.gt), ValueError, "Check x-member>10")
@raise_if_false_on_class(member_enforcer('library_functionality', types.FunctionType), AttributeError)
class HasCorrectMethodAndInstanceVarCheckClass(metaclass=HasRulesActions):
    def __init__(self, value=20):
        self.x = value
    def library_functionality(self):
        return 1
```

If we wanted to ensure that a static set had a minimum number of instances of each type (e.g., 1 `string`, 2 `int` and 1 `float`):

```python
from collections import Counter
from collections.abc import Iterable

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


@raise_if_false_on_class(partial(min_list_type_counter, 
                                 list_name='STATIC_SET', 
                                 min_counter = Counter({str: 1, int: 2, float:1})), 
                         AttributeError)
class HasClassLevelMemberTypeCheckClass(metaclass=HasRulesActions):
    STATIC_SET = ("Test", 10, 40, 50, 45.5, 60.0, '3', 'i', BaseException())

```
If we wanted to raise an exception as soon as a member value reaches the value 10 during the course of the process:
```python
@raise_if_false_on_instance(lambda x: x.y<10, ValueError)
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
a.add(10)  # will raise a ValueError

```

To illustrate the triggering of functionality we create the following contrived example: a `ProducerClass` manages an integer resource that has be >=0 and <100. Every time a value larger than or equal to 20 is produced, it passes the value to an instance of `LargeNumberProcessor`. If the latter is passed a value larger than or equal to 50 it raises an exception. If the average of unprocessed values in its list is larger than or equal to 30, all of the values to process will get halved.

```python
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
```

An example run would then be:

```python
k = ProducerClass()
k.add(5)
k.add(5)
k.add(5)
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
k.add(40)  # will raise a ValueError as we try to pass 61>=50 to the LargeNumberProcessor
```
Note that `run_if_false_on_instance` only takes 2 arguments: a predicate function taking the instance as an argument and the function that will be executed should the predicate be false. The latter takes the instance as an argument[^7].

When using multiple decorators in general, one must be aware that the order of decorator matters with decorator closest to the function/class applied first. With multiple decorator we must also avoid clashes between decorators.

Though not intended for this use, the enforced rules (through predicate functions) are available through the `EnforcedFunctions` static class and can thus be retrieved, applied and transferred at any point in the code.

[^1]: The functionality itself is up to the user. Possible suggestions could be callback mechanisms, logging, asynchronous tasks, etc.
[^2]: By default, rules and actions on instances are enforced after creation of an instance only. It is possible use these rules and actions after any member function call by using the `run_instance_`-style decorator on the method.
[^3]: Here we refer to interactions with the `dataclasses` and `property` decorators 
[^4]: The second argument will be used to examine class attributes when required. Note that by always providing a second argument and defaulting it to `None` (as was done in `key_type_enforcer`), the function can be used both on instances and class declarations.
[^5]: Note that this is an exception type and not an instance. For rules on classes this defaults to `AttributeError`, for rules of instantiation this defaults to `ValueError`. Other exceptions or classes (including user defined ones) can be supplied, provided instances can be constructed from a string 
[^6]: `member_enforcer` has 2 compulsory arguments: the `enforced_key` (a string with the attribute name) and the `enforced_type` (the type of the attribute) and 2 optional arguments: the `comparison_value` and the `operator_used`, the latter defaults to the boolean equality operator and is only applied if a value is provided.
[^7]: additional arguments can be bound using methods like `partial`
