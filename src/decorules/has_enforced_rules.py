import types
from collections import defaultdict
import types
from collections import defaultdict
from utils import false_on_raise_else_true


class HasEnforcedRules(type):

    def __new__(cls,
                name_of_class: str,
                baseclasses: tuple,
                attrs: dict
                ):
        cls_instance = super().__new__(cls, name_of_class, baseclasses, attrs)
        # print(f"Class {name_of_class} created") we allow the derived classes to create a type CLASS instance however
        # they see fit and check any class level checks here
        # base classes will get their own call with their own attribute dict if the right metaclass
        EnforcedFunctions.run_functions_applied_to_class(cls_instance, attrs)
        # print(f"Class {name_of_class} and {baseclasses} checked")
        return cls_instance

    def __call__(cls,
                 *args,
                 **kwargs):
        # Create an object instance
        instance = super().__call__(*args, **kwargs)
        # print(f"Instance of {cls.__name__} created") we allow the derived classes to create an class instance
        # however they see fit and check any instance level checks here
        EnforcedFunctions.run_functions_applied_to_instance(instance)
        # all of them need to be checked at every instance creation!
        # print(f"Instance of {cls.__name__} checked")
        return instance


class EnforcedFunctions:
    _functions_applied_to_instance = defaultdict(list)
    _functions_applied_to_class = defaultdict(list)

    @classmethod
    def _apply_functions_applied_to_class(cls, cls_instance: type, attrs: dict = None):
        if cls._functions_applied_to_class[cls_instance.__name__]:
            for func in cls._functions_applied_to_class[cls_instance.__name__]:
                func(cls_instance, attrs)
                print(f"PASSED {func.__name__} applied to class {cls_instance.__name__}")

    @classmethod
    def _apply_functions_applied_to_instance(cls, instance, cls_key: str):
        if cls._functions_applied_to_instance[cls_key]:
            for func in cls._functions_applied_to_instance[cls_key]:
                func(instance)
                print(f"PASSED {func.__name__} applied to instance {str(instance)}")

    @classmethod
    def add_enforce_function_to_class(cls,
                                      cls_key: str,
                                      func: types.FunctionType):
        cls._functions_applied_to_class[cls_key].append(func)

    @classmethod
    def add_enforce_function_to_instance(cls,
                                         cls_key: str,
                                         func: types.FunctionType):
        cls._functions_applied_to_instance[cls_key].append(func)
        print((cls_key, len(cls._functions_applied_to_instance[cls_key])))

    @classmethod
    def run_functions_applied_to_class(cls,
                                       cls_instance: type,
                                       attrs: dict = None):
        if len(cls._functions_applied_to_class) > 0:
            cls._apply_functions_applied_to_class(cls_instance, attrs)
            # the bases will get called individually with their own attrs if they are of type HasEnforcedRules
            # print(self._functions_applied_to_class)
            # classes_to_check = [cls_instance]
            # if bases is not None:
            #     classes_to_check.extend([x for x in bases if isinstance(x, type)])
            # for x in classes_to_check:
            #     cls._apply_functions_applied_to_class(x)

    @classmethod
    def run_functions_applied_to_instance(cls, instance):
        if not issubclass(type(type(instance)), HasEnforcedRules):
            raise ValueError(
                f"Attempt to check functions_applied_to_instance applied on an instance of {type(instance)}, "
                f"which is not of HasEnforcedRules type")
        # for the instance functions we do need to loop through all the bases
        if len(cls._functions_applied_to_instance) > 0:
            # print(self._functions_applied_to_instance)
            cls_keys = [type(instance).__name__]
            bases = [x.__name__ for x in type(instance).__bases__]
            if bases is not None:
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
