class Event(object):
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        return EventHandler(self, obj) if obj else self

    def __set__(self, obj, value):
        pass


class EventHandler(object):
    def __init__(self, event, obj):
        self.event = event
        self.obj = obj

    def _getfunctionlist(self):
        """(internal use) """
        try:
            eventhandler = self.obj.__eventhandler__
        except AttributeError:
            eventhandler = self.obj.__eventhandler__ = {}
        return eventhandler.setdefault(self.event, [])

    def add(self, func):
        """Add new event handler function.

        Event handler function must be defined like func(sender, earg).
        You can add handler also by using '+=' operator.
        """
        self._getfunctionlist().append(func)
        return self

    def remove(self, func):
        try:
            self._getfunctionlist().remove(func)
        except ValueError:
            print("Trying to remove the method ", func, "from event handler of class", self.obj,
                  "when it was not subscribed")
        return self

    def fire(self, *args, **kwargs):
            [func(self.obj, *args, **kwargs) for func in self._getfunctionlist()]

    def get_listeners_count(self):
        listeners = self._getfunctionlist()
        return len(listeners) if listeners else 0

    __iadd__ = add
    __isub__ = remove
    __call__ = fire
    __len__ = get_listeners_count
