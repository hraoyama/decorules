import types
from collections import defaultdict
import types
from collections import defaultdict
from decorules.utils import false_on_raise_else_true


class HasEnforcedRules(type):

    def __call__(cls,
                 *args,
                 **kwargs):
        # Create an object instance
        instance = super().__call__(*args, **kwargs)
        # We allow the derived classes to create an class instance
        # however they see fit and check any instance level checks here
        # all of them need to be checked at every instance creation!
        EnforcedFunctions.run_functions_applied_to_instance(instance)
        return instance


class EnforcedFunctions:
    _functions_applied_to_instance = defaultdict(set)
    _functions_applied_to_class = defaultdict(set)

    @classmethod
    def _apply_functions_applied_to_class(cls, cls_instance: type, attrs: dict = None):
        if cls._functions_applied_to_class[cls_instance.__name__]:
            for func in cls._functions_applied_to_class[cls_instance.__name__]:
                func(cls_instance, attrs)
            pass
        pass

    @classmethod
    def _apply_functions_applied_to_instance(cls, instance, cls_key: str):
        if cls._functions_applied_to_instance[cls_key]:
            for func in cls._functions_applied_to_instance[cls_key]:
                func(instance)
            pass
        pass

    @classmethod
    def add_enforce_function_to_class(cls,
                                      cls_key: str,
                                      func):
        cls._functions_applied_to_class[cls_key].add(func)

    @classmethod
    def add_enforce_function_to_instance(cls,
                                         cls_key: str,
                                         func):
        cls._functions_applied_to_instance[cls_key].add(func)

    @classmethod
    def run_functions_applied_to_class(cls,
                                       cls_instance: type,
                                       attrs: dict = None):
        if len(cls._functions_applied_to_class) > 0:
            cls._apply_functions_applied_to_class(cls_instance, attrs)
            # the bases will get called individually with their own attrs if they are of type HasEnforcedRules

    @classmethod
    def run_functions_applied_to_instance(cls, instance):
        if not issubclass(type(type(instance)), HasEnforcedRules):
            raise TypeError(
                f"Attempt to check functions_applied_to_instance applied on an instance of {type(instance)}, "
                f"which is not of HasEnforcedRules type")
        # for the instance functions we must loop through all the bases
        if len(cls._functions_applied_to_instance) > 0:
            cls_keys = [type(instance).__name__]
            bases = [x.__name__ for x in type(instance).__bases__ if x.__name__ != 'object']
            if bases:
                cls_keys.extend(bases)
            for cls_key in cls_keys:
                cls._apply_functions_applied_to_instance(instance, cls_key)

    @classmethod
    def get_functions_applied_instance(cls, class_name: str):
        return cls._functions_applied_to_instance[class_name]

    @classmethod
    def get_functions_applied_class(cls, class_name: str):
        return cls._functions_applied_to_class[class_name]

    @classmethod
    def revert_to_boolean_returns(cls, class_names=None):
        """
        Returns a tuple which for the supplied class names (defaults to all class names) with the first element:
        a dictionary with the class names as keys and as values the list of functions checking class structure
        but returning True if the check passed and False if the original check function had thrown an
        exception with the second element: a dictionary with the class names as keys and as values the list of
        functions checking a class instance but returning True if the check passed and False if the original check
        function had thrown an exception This is not used yet, but could be part of run-time transfer of
        rules between classes.

        :param class_names: The class names that are the keys of the original dictionary. Note that if an entire
        class hierarchy is required all base classes (that could have enforced rules) needs to be supplied :type
        class_names: a container type that allows the use of 'in', i.e. overloads __contains__
        """
        if class_names is None:
            class_names = list(cls._functions_applied_to_class.keys()) + list(
                cls._functions_applied_to_instance.keys())

        return (
            {key: [false_on_raise_else_true(func) for func in cls._functions_applied_to_class[key]] for key, _ in
             cls._functions_applied_to_class.items() if key in class_names},
            {key: [false_on_raise_else_true(func) for func in cls._functions_applied_to_instance[key]] for key, _ in
             cls._functions_applied_to_instance.items() if key in class_names}
        )
