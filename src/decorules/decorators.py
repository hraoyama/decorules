import types
from typing import Type
from functools import wraps
from decorules.has_enforced_rules import HasEnforcedRules, EnforcedFunctions


def _raise_error_if_false(enforced_function: types.FunctionType,
                          exception_type: Type[BaseException],
                          on_class: bool = True,
                          extra_info: str = None):
    if extra_info is None:
        extra_info = ''

    def raise_when_false(cls, function_name):
        @wraps(enforced_function)
        def wrapped_raise_when_false(*args, **kwargs):
            if on_class:
                # if on a class, we need to check if attributes dictionary got passed
                # if it did it needs to go on the kwargs
                if len(args) > 1:
                    # attrs should be the only dictionary argument
                    dict_args = [x for x in args if isinstance(x, dict)]
                    if len(dict_args) > 1:
                        raise ValueError("Class enforcing function was called with more than one dictionary argument "
                                         "(reserved for attributes)")
                    else:
                        kwargs['attrs'] = dict_args[0]
                        args = tuple(x for x in args if x != dict_args[0])
            if enforced_function(*args, **kwargs) is False:
                if on_class:
                    error_str = (f"{extra_info} {cls.__class__.__name__} fails class check {function_name} will "
                                 f"raise {exception_type.__qualname__}").strip()
                else:
                    error_str = (f"{extra_info} {cls.__class__.__name__} fails instance check {function_name} will "
                                 f"raise {exception_type.__qualname__}").strip()
                exception_instance = eval(f'{exception_type.__qualname__}("{error_str}")')
                raise exception_instance

        return wrapped_raise_when_false

    if on_class:
        def wrapped_class(cls):
            if 'HasEnforcedRules' not in type(cls).__name__:
                # not issubclass(type(cls), HasEnforcedRules):
                raise TypeError(
                    f"{cls.__class__.__name__} must be of type {HasEnforcedRules.__class__.__name__} in order to "
                    f"use the decorator _raise_error_if_false")
            function_name = str(enforced_function)
            func_to_add = raise_when_false(cls, function_name)
            EnforcedFunctions.add_enforce_function_to_class(cls.__name__, func_to_add)
            func_to_add(cls)
            return cls

        return wrapped_class
    else:
        def function_that_adds_check_instance_class(cls):
            if 'HasEnforcedRules' not in type(cls).__name__:
                raise TypeError(
                    f"{cls.__class__.__name__} must be of type {HasEnforcedRules.__class__.__name__} in order to use "
                    f"the decorator raiseErrorIfFalse on instance creation")
            function_name = str(enforced_function)
            EnforcedFunctions.add_enforce_function_to_instance(cls.__name__,
                                                               raise_when_false(cls, function_name))
            # this now needs to be checked at every instance not on class type instantiation
            return cls

        return function_that_adds_check_instance_class
    pass


def raise_if_false_on_class(enforced_function: types.FunctionType,
                            exception_type: Type[BaseException] = Type[AttributeError],
                            extra_info: str = None):
    return _raise_error_if_false(enforced_function,
                                 exception_type,
                                 on_class=True,
                                 extra_info=extra_info)


def raise_if_false_on_instance(enforced_function: types.FunctionType,
                               exception_type: Type[BaseException] = Type[ValueError],
                               extra_info: str = None):
    return _raise_error_if_false(enforced_function,
                                 exception_type,
                                 on_class=False,
                                 extra_info=extra_info)


def enforces_instance_rules(input_method):
    @wraps(input_method)
    def wrapped_method(self, *args, **kwargs):
        input_method(self, *args, **kwargs)
        EnforcedFunctions.run_functions_applied_to_instance(self)

    return wrapped_method
