import types
from typing import Type
from functools import wraps, partial
from decorules.has_rules_actions import HasRulesActions, EnforcedFunctions
from decorules.utils import Purpose


def _construct_and_raise(exception_type: Type[BaseException], *args, **kwargs):
    raise exception_type(*args, **kwargs)


def _run_func_if_false(enforced_function: types.FunctionType,
                       executed_function: types.FunctionType = partial(_construct_and_raise, Type[BaseException]),
                       on_class: bool = True,
                       extra_info: str = None,
                       purpose: Purpose = Purpose.RULE):
    if extra_info is None:
        extra_info = ''

    def run_func_when_false(cls, function_name):
        @wraps(enforced_function)
        def wrapped_run_func_when_false(*args, **kwargs):
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
                if purpose == Purpose.RULE:
                    error_str = f"{extra_info} {cls.__class__.__name__} fails {'class' if on_class else 'instance'} check {function_name}".strip()
                    executed_function(error_str)
                elif purpose == Purpose.ACTION:
                    executed_function(args[0])  # note not cls as cls is the type, we need the instance

        return wrapped_run_func_when_false

    if on_class:
        def wrapped_class_with_enforced_rules(cls):
            if not issubclass(type(cls), HasRulesActions):
                raise TypeError(
                    f"{cls.__class__.__name__} must be of type {HasRulesActions.__class__.__name__} in order to "
                    f"use a decorules decorator")
            function_name = str(enforced_function)
            func_to_add = run_func_when_false(cls, function_name)
            EnforcedFunctions.add_enforce_function_to_class(cls.__name__, func_to_add)
            func_to_add(cls)
            return cls

        return wrapped_class_with_enforced_rules
    else:
        def wrapped_func_adding_check_to_instance_or_class(cls):
            if not issubclass(type(cls), HasRulesActions):
                raise TypeError(
                    f"{cls.__class__.__name__} must be of type {HasRulesActions.__class__.__name__} in order to use "
                    f"the decorator raiseErrorIfFalse on instance creation")
            function_name = str(enforced_function)
            EnforcedFunctions.add_enforce_function_to_instance(cls.__name__,
                                                               run_func_when_false(cls, function_name),
                                                               purpose)
            # this now needs to be checked at every instance not on class type instantiation
            return cls

        return wrapped_func_adding_check_to_instance_or_class
    pass


def raise_if_false_on_class(enforced_function: types.FunctionType,
                            exception_type: Type[BaseException] = Type[AttributeError],
                            extra_info: str = None):
    return _run_func_if_false(enforced_function,
                              partial(_construct_and_raise, exception_type),
                              on_class=True,
                              extra_info=extra_info,
                              purpose=Purpose.RULE)


def raise_if_false_on_instance(enforced_function: types.FunctionType,
                               exception_type: Type[BaseException] = Type[ValueError],
                               extra_info: str = None):
    # do not use exception_type=exception_type in the below (confuses python)
    return _run_func_if_false(enforced_function,
                              partial(_construct_and_raise, exception_type),
                              on_class=False,
                              extra_info=extra_info,
                              purpose=Purpose.RULE)


def run_if_false_on_instance(enforced_function: types.FunctionType,
                             executed_function: types.FunctionType):
    # do not use exception_type=exception_type in the below (confuses python)
    return _run_func_if_false(enforced_function,
                              executed_function,
                              on_class=False,
                              extra_info=None,
                              purpose=Purpose.ACTION)


def run_instance_rules(input_method):
    @wraps(input_method)
    def wrapped_method(self, *args, **kwargs):
        input_method(self, *args, **kwargs)
        EnforcedFunctions.run_functions_applied_to_instance(self, Purpose.RULE)

    return wrapped_method


def run_instance_actions(input_method):
    @wraps(input_method)
    def wrapped_method(self, *args, **kwargs):
        input_method(self, *args, **kwargs)
        EnforcedFunctions.run_functions_applied_to_instance(self, Purpose.ACTION)

    return wrapped_method
