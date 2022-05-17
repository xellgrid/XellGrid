from itertools import chain
from traitlets import (
    All,
    parse_notifier_name
)


class EventHandlers(object):

    def __init__(self):
        self._listeners = {}

    def on(self, names, handler):
        names = parse_notifier_name(names)
        for n in names:
            self._listeners.setdefault(n, []).append(handler)

    def off(self, names, handler):
        names = parse_notifier_name(names)
        for n in names:
            try:
                if handler is None:
                    del self._listeners[n]
                else:
                    self._listeners[n].remove(handler)
            except KeyError:
                pass

    def notify_listeners(self, event, qgrid_widget):
        event_listeners = self._listeners.get(event['name'], [])
        all_listeners = self._listeners.get(All, [])
        for c in chain(event_listeners, all_listeners):
            c(event, qgrid_widget)