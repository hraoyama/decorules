from functools import wraps, partial
import operator


def member_enforcer(enforced_key: str,
                    enforced_type: type,
                    comparison_value=None,
                    operator_used=operator.eq,
                    attrs_used: dict = None):
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
