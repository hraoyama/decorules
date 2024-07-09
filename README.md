# decorules

_decorules_ is a tiny library that seeks to enforce class structure and instance behaviour on classes and their derived classes through decorators at class declaration time. Useful for library developers.

The rules are specified through __decorators on the class declaration__ and using the metaclass __HasEnforcedRules__ from the library. Enforcement of the rules is done by throwing exceptions (which can be developer specified) when a predicate function fails on the class or an instance (depending on the decorator used).

In the case of rules enforced on instances, these are enforced on creation of an instance only. The rules are available throughout and can thus be applied at any point in time.

## Simple Examples

Let us start with a requirement that a class or an instance must have an attribute of a certain type. Here are the basic steps:

  - Create a function that takes a class or an instance and checks whether an attribute exists and is of the correct type. In the example, this function is `key_type_enforcer1`
```python
from functools import partial

def key_type_enforcer1(instance_object, enforced_type: type, enforced_key: str):
    member_object = getattr(instance_object, enforced_key, None)
    if member_object is None:
        return False
    return type(member_object) == enforced_type
```

  - If the function is not already a [predicate](https://stackoverflow.com/questions/1344015/what-is-a-predicate) (which it is not in our example), turn it into one using any preferred method (e.g., `partial` from the `functools` package)
  - Use the decorator `raiseErrorIfFalseOnClass` when enforcing a rule on a class level, or `raiseErrorIfFalseOnInstance` when enforcing upon instantiation. 

To guarantee that a new class (and its derived classes) implements a function named `library_functionality`:

```python
from decorules import HasEnforcedRules
import types
@raiseErrorIfFalseOnClass(partial(key_type_enforcer1, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class NormalLibraryClass(metaclass=HasEnforcedRules):
    def library_functionality(self):
        return 1
```

If in addition, we ensure that every instance had an `int` member `x`:

```python
@raiseErrorIfFalseOnInstance(partial(key_type_enforcer1, enforced_type=int, enforced_key='x'), AttributeError)  
@raiseErrorIfFalseOnClass(partial(key_type_enforcer1, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class NormalLibraryClass(metaclass=HasEnforcedRules):
    def __init__(self, value=20):
        self.x = value
    def library_functionality(self):
        return 1
```

Should the `__init__` implementation not set `self.x` or remove it using `del self.x`, all of the following instantitiation would throw an `AttributeError`:
```python
a = NormalLibraryClass()
b = NormalLibraryClass(25)
c = NormalLibraryClass(5)
```
For forcing `x` to be larger than 10:
```python
@raiseErrorIfFalseOnInstance(partial(key_type_enforcer1, enforced_type=int, enforced_key='x'), AttributeError)  
@raiseErrorIfFalseOnInstance(lambda ins: ins.x > 10, ValueError, "Check x-member>10")  
@raiseErrorIfFalseOnClass(partial(key_type_enforcer1, enforced_type=types.FunctionType, enforced_key='library_functionality'), AttributeError)
class NormalLibraryClass(metaclass=HasEnforcedRules):
    def __init__(self, value=20):
        self.x = value
    def library_functionality(self):
        return 1
```
Note the third argument in the decorator, this optional argument is prependend to the message of the exception. Here it is used to provide more explanation on the predicate.
Only the third line would raise an exception:

```python
a = NormalLibraryClass()
b = NormalLibraryClass(25)
c = NormalLibraryClass(5) # a ValueError is raised
```

If we wanted to ensure that a static list had a number of instances of each type (e.g., 1 `string`, 2 `int` and 1 `float`):

```python
from collections import Counter
from collections.abc import Iterable

def min_list_type_counter(instance_object, list_name: str, min_counter: Counter):
    member_object = getattr(instance_object, list_name, None)
    if member_object is None:
        return False
    if isinstance(member_object, Iterable):
        return Counter(type(x) for x in member_object) >= min_counter
    else:
        return False

@raiseErrorIfFalseOnClass(partial(min_list_type_counter, list_name='STATIC_LIST', min_counter = Counter({str: 1, int: 2, float:1})), AttributeError)
class NormalLibraryClass(metaclass=HasEnforcedRules):
    STATIC_LIST = ("Test", 10, 40, 50, 45.5, 60.0, '3', 'i', BaseException())

```
When using multiple decorators in general, one must be aware that the order of decorator matters with decorator closest to the function/class applied last. With multiple decorator we must also avoid clashes between decorators.
