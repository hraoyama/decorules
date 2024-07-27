from functools import wraps, partial
import operator


def member_enforcer(enforced_key: str,
                    enforced_type: type,
                    comparison_value=None,
                    operator_used=operator.eq,
                    attrs_used: dict = None):
    """
    member_enforcer

    The member_enforcer function is a factory that creates a custom enforcement function to validate attributes of objects or classes. It checks if an attribute (specified by enforced_key) exists and meets certain conditions, including type checking and comparison operations.
    Parameters

    :param enforced_key (str):The name of the attribute (member) to be checked on the instance or class.
    :param enforced_type (type): The expected type of the attribute. The attribute's type must be a subclass of this type for the check to pass.
    :param comparison_value (optional, default: None): A value to compare the attribute against. If provided, the comparison is performed using the operator_used function.
    :param operator_used (optional, default: operator.eq): A function used to compare the attribute's value with comparison_value. Defaults to equality (operator.eq). Other examples include operator.lt for less than, operator.gt for greater than, etc.
    :param attrs_used (optional, default: None): A dictionary providing fallback attributes. If the primary attribute (enforced_key) is not found on the object, the function will look it up in this dictionary. Used for checking the static attributes of a class
    :return: bool
    """

    def key_type_comparison_enforcer(instance_or_type,
                                     enforced_type: type,
                                     enforced_key: str,
                                     comparison_value=comparison_value,
                                     operator_used=operator_used,
                                     attrs_used=attrs_used):
        member_object = getattr(instance_or_type, enforced_key, None)
        if member_object is None:
            if attrs_used is not None:
                member_object = attrs_used.get(enforced_key, None)
        if member_object is None:
            return False
        else:
            if issubclass(type(member_object), enforced_type):
                if comparison_value is not None and operator_used is not None:
                    return operator_used(member_object, comparison_value)
                else:
                    return True
            else:
                return False
        pass

    return partial(key_type_comparison_enforcer,
                   enforced_type=enforced_type,
                   enforced_key=enforced_key,
                   comparison_value=comparison_value,
                   operator_used=operator_used,
                   attrs_used=attrs_used)


def false_on_raise_else_true(func):
    # will be used when we 'transfer' enforced rules
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except Exception as ex:
            return False

    return func_wrapper
