from functools import wraps

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

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