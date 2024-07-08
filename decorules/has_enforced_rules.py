from collections import defaultdict
from decorules_utils import singleton, false_on_raise_else_true

class HasEnforcedRules(type):

    # it is better to put the EnforcedFunctions Static Data in a separate class so the successive decorators on classes do not obfuscate this
    @singleton
    class EnforcedFunctions:
        def __init__(self):
            print("Creating the EnforcedFunctions Singleton instance")
            self._functions_applied_to_instance = defaultdict(list)
            self._functions_applied_to_class = defaultdict(list)

        def _apply_functions_applied_to_class(self, cls_instance: type):
            if self._functions_applied_to_class[cls_instance.__name__]:
                for func in self._functions_applied_to_class[cls_instance.__name__]:
                    func(cls_instance)
                    print(f"PASSED {func.__name__} applied to class {cls_instance.__name__}")

        def _apply_functions_applied_to_instance(self, instance, cls_key: str):
            if self._functions_applied_to_instance[cls_key]:
                for func in self._functions_applied_to_instance[cls_key]:
                    func(instance)
                    print(f"PASSED {func.__name__} applied to instance {str(instance)}")

        def add_enforce_function_to_class(self, cls_key: str, func: types.FunctionType):
            self._functions_applied_to_class[cls_key].append(func)

        def add_enforce_function_to_instance(self, cls_key: str, func: types.FunctionType):
            self._functions_applied_to_instance[cls_key].append(func)

        def run_functions_applied_to_class(self, cls_instance: type, bases: tuple = None):
            if len(self._functions_applied_to_class)>0:
                print(self._functions_applied_to_class)
                classes_to_check = [cls_instance]
                if bases is not None:
                    classes_to_check.extend([x for x in bases if isinstance(x,type)])
                for x in classes_to_check:
                    self._apply_functions_applied_to_class(x)
                
        def run_functions_applied_to_instance(self, instance):
            if not issubclass(type(type(instance)), HasEnforcedRules):
                raise ValueError(f"Attempt to check functions_applied_to_instance applied on an instance of {type(instance)}, which is not of HasEnforcedRules type")
            if len(self._functions_applied_to_instance)>0:
                print(self._functions_applied_to_instance)
                cls_keys = [type(instance).__name__]
                bases = [x.__name__ for x in type(instance).__bases__]
                if bases is not None:
                    cls_keys.extend(bases)
                for cls_key in cls_keys:
                    self._apply_functions_applied_to_instance(instance, cls_key)

        def get_functions_applied_instance(self, class_name: str):
            return self._functions_applied_to_instance[class_name]             

        def get_functions_applied_class(self, class_name: str):
            return self._functions_applied_to_class[class_name]             

        def revert_to_boolean_returns(self, class_names = None):
            """
            Returns a tuple which for the supplied class names (defaults to all class names) 
                with the first element: a dictionary with the class names as keys and as values the list of functions checking class structure but returning True if the check passed and False if the orginal check function would have thrown an exception
                with the second element: a dictionary with the class names as keys and as values the list of functions checking a class instance but returning True if the check passed and False if the orginal check function would have thrown an exception
            This is not used yet, but could be part of run-time transfer of rules between classes.

            :param class_names: The class names that are the keys of the orginal dictionary. Note that if an entire class hierarchy is required all base classes (that could have enforced rules) needs to be supplied
            :type class_names: a container type that allows the use of 'in', i.e. overloads __contains__
            """
            if class_names is None:
                class_names = list(self._functions_applied_to_class.keys()) + list(self._functions_applied_to_instance.keys())             

            return ( { key: [ false_on_raise_else_true(func) for func in self._functions_applied_to_class[key] ] for key, _ in self._functions_applied_to_class.items() if key in class_names  }, 
                     { key: [ false_on_raise_else_true(func) for func in self._functions_applied_to_instance[key] ] for key, _ in self._functions_applied_to_instance.items() if key in class_names }
                    )
            
    def __new__(cls, classname : str, baseclasses: tuple, attrs: dir):
        cls_instance = super().__new__(cls, classname, baseclasses, attrs) 
        print(f"Class {classname} created")
        # we allow the derived classes to create a type CLASS instance however they see fit and check any class level checks here
        HasEnforcedRules.EnforcedFunctions().run_functions_applied_to_class(cls_instance, baseclasses)
        print(f"Class {classname} and {baseclasses} checked")
        return cls_instance
    
    def __call__(cls, *args, **kwargs):
        # Create an object instance
        instance = super().__call__(*args, **kwargs)
        print(f"Instance of {cls.__name__} created")
        # we allow the derived classes to create an class instance however they see fit and check any instance level checks here
        HasEnforcedRules.EnforcedFunctions().run_functions_applied_to_instance(instance)  # all of them need to be checked at every instance creation!
        print(f"Instance of {cls.__name__} checked")
        return instance
