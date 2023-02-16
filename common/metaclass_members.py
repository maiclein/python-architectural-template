import collections


class OrderedClass(type):

    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, namespace, **kwds):
        result = type.__new__(mcs, name, bases, dict(namespace))
        result.members = tuple(namespace)
        result.this_class_name = name.lower()
        return result
