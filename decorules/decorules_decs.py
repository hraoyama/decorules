import types
from functools import wraps
from has_enforced_rules import HasEnforcedRules

def raiseErrorIfFalse(enforced_function : types.FunctionType, exception_type : BaseException, on_class : bool = True, extra_info : str = None):
    if extra_info is None:
        extra_info = ''

    @wraps(enforced_function)      
    def raise_when_false(cls, function_name):
        def raise_when_false(*args, **kwargs):
            if enforced_function(*args, **kwargs) is False:
                if on_class:
                    error_str = f"{extra_info} {cls.__class__.__name__} fails class level check {function_name} will raise {exception_type.__qualname__}"
                else:
                    error_str = f"{extra_info} {cls.__class__.__name__} fails instance level check {function_name} will raise {exception_type.__qualname__}"
                exception_instance = eval(f'{exception_type.__qualname__}("{error_str}")')
                raise exception_instance
        return raise_when_false

    # an alternative to this if/else split is to implement a wraps for classes such that the function checks on instances could get routed correctly
    if on_class:        
        def wrapped_class(cls):
            if not isinstance(cls, HasEnforcedRules):
                raise AttributeError(f"{cls.__class__.__name__} must be derived from {HasEnforcedRules.__class__.__name__} in order to use the decorator raiseErrorIfFalse")
            class WrappedClass(cls):
                function_name = str(enforced_function)
                print(f"Adding {function_name} to check functions, for {cls.__name__}")
                func_to_add = raise_when_false(cls, function_name)
                HasEnforcedRules.EnforcedFunctions().add_enforce_function_to_class(cls.__name__, func_to_add)
                func_to_add(cls) # now that we have type class, we must check it here and not loop through every required function 
            return WrappedClass
        return wrapped_class    
    else:
        def function_that_adds_check_instance_class(cls):
            if not issubclass(type(cls), HasEnforcedRules):
                raise AttributeError(f"{cls.__class__.__name__} must be of type {HasEnforcedRules.__class__.__name__} in order to use the decorator raiseErrorIfFalse on instance creation")
            function_name = str(enforced_function)
            HasEnforcedRules.EnforcedFunctions().add_enforce_function_to_instance(cls.__name__, raise_when_false(cls, function_name))  
            # this now needs to be checked at every instance not on class type instantiation
            return cls        
        return function_that_adds_check_instance_class
    pass

def raiseErrorIfFalseOnClass(enforced_function : types.FunctionType, exception_type : BaseException = AttributeError, extra_info : str = None):
    return raiseErrorIfFalse(enforced_function, exception_type, on_class = True, extra_info=extra_info)

def raiseErrorIfFalseOnInstance(enforced_function : types.FunctionType, exception_type : BaseException  = ValueError, extra_info : str = None):
    return raiseErrorIfFalse(enforced_function, exception_type, on_class = False, extra_info=extra_info)
