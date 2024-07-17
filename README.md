# decorules

## Introduction

_decorules_ is a tiny python library that seeks to enforce rules on class structure and instantiation behavior for classes and class hierarchies through decorators at the point of class declaration. 

The primary objective is to help library developers enforce behavior on derived classes. Secondary benefits are defensive measures, for instance to quickly have an overview of any structural rules enforced on the class.

The rules are specified through __decorators on the class declaration__ and using the metaclass __HasEnforcedRules__ from the library. Enforcement of the rules is done by throwing exceptions (which can be developer specified) when a predicate function fails on the class or an instance (depending on the decorator used).

In the case of rules enforced on instances, these are enforced on creation of an instance only. 


## Installation

_decorules_ was built using python `3.10`. It is available as a [package on pypi](https://pypi.org/project/decorules/) and can be installed through pip:

```
pip install decorules
```
Should you require an installation of pip, follow the instructions on the [pip website](https://pip.pypa.io/en/stable/installation/).

## Examples

A worked out example of a class hierachry can be found under `src/example`, with `library_class.py` and `client_class.py` representing the library and client respectively.

Further examples can be found under the test directory. 

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

2. For restrictions on instances, the function must be [predicate](https://stackoverflow.com/questions/1344015/what-is-a-predicate). This means the function takes one argument (the instance) and returns a boolean. Functions can be turned into predicates using different methods, in this example we will use `partial` from the `functools` package). For restrictions on classes that do not check the values of attributes (e.g., check if a static float is positive) predicate functions can be provided. If the rule on the class does make use of such a value, the function must take 2 arguments and return a boolean. The second argument should always default to `None`[^1].  
3. Use the decorator `raise_if_false_on_class` when enforcing a rule on a class level, or `raise_if_false_on_instance` when enforcing upon instantiation. Both decorators take 1 compulsory argument (the function from 2. that return a True/False value) and 2 optional arguments, the first is the type of the exception to be raised should the rule not hold[^2] and the second optional argument is a string providing extra information when the exception is raised.

In order to guarantee that the class (and its derived classes) implements a function named `library_functionality` we would implement:

```python
from decorules import HasEnforcedRules
import types
from functools import partial

@raise_if_false_on_class(partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class HasCorrectMethodClass(metaclass=HasEnforcedRules):
    def library_functionality(self):
        return 1
```

If in addition, we ensure that an `int` member named `x` existed after every instantiation:

```python
@raise_if_false_on_instance(partial(key_type_enforcer, enforced_type=int, enforced_key='x'), AttributeError)  
@raise_if_false_on_class(partial(key_type_enforcer, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class HasCorrectMethodAndInstanceVarClass(metaclass=HasEnforcedRules):
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
class HasCorrectMethodAndInstanceVarCheckClass(metaclass=HasEnforcedRules):
    def __init__(self, value=20):
        self.x = value
    def library_functionality(self):
        return 1
```
Note the third argument in the decorator, this will be prependend to the message of the exception. 
For the implementation above, only the third line would raise an exception:

```python
a = HasCorrectMethodAndInstanceVarCheckClass()
b = HasCorrectMethodAndInstanceVarCheckClass(25)
c = HasCorrectMethodAndInstanceVarCheckClass(5) # a ValueError is raised
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


@raise_if_false_on_class(partial(min_list_type_counter, list_name='STATIC_SET', min_counter = Counter({str: 1, int: 2, float:1})), AttributeError)
class HasClassLevelMemberTypeCheckClass(metaclass=HasEnforcedRules):
    STATIC_SET = ("Test", 10, 40, 50, 45.5, 60.0, '3', 'i', BaseException())

```

When using multiple decorators in general, one must be aware that the order of decorator matters with decorator closest to the function/class applied first. With multiple decorator we must also avoid clashes between decorators.

Though not intended for this use, the enforced rules (through predicate functions) are available through the `EnforcedFunctions` static class and can thus be retrieved, applied and transferred at any point in the code.

[^1]: The second argument will be used to examine class attributes when required. Note that by always providing a second argument and defaulting it to `None` (as was done in `key_type_enforcer`), the function can be used both on instances and class declarations.
[^2]: Note that this is an exception type and not an instance. For rules on classes this defaults to `AttributeError`, for rules of instantiation this defaults to `ValueError`. Other exceptions or classes (including user defined ones) can be provided if they can be constructed from a string 
