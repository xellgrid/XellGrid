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

    def notify_listeners(self, event, xellgrid_widget):
        event_listeners = self._listeners.get(event['name'], [])
        all_listeners = self._listeners.get(All, [])
        for c in chain(event_listeners, all_listeners):
            c(event, xellgrid_widget)


def on(names, handler):
    """
    Setup a handler to be called when a user interacts with any xellgrid instance.

    Parameters
    ----------
    names : list, str, All
        If names is All, the handler will apply to all events.  If a list
        of str, handler will apply to all events named in the list.  If a
        str, the handler will apply just the event with that name.
    handler : callable
        A callable that is called when the event occurs. Its
        signature should be ``handler(event, xellgrid_widget)``, where
        ``event`` is a dictionary and ``xellgrid_widget`` is the XellgridWidget
        instance that fired the event. The ``event`` dictionary at least
        holds a ``name`` key which specifies the name of the event that
        occurred.

    Notes
    -----
    There is also an ``on`` method on each individual XellgridWidget instance,
    which works exactly like this one except it only listens for events on an
    individual instance (whereas this module-level method listens for events
    on all instances).

    See that instance-level method (linked below) for a list of all events
    that can be listened to via this module-level ``on`` method.  Both
    methods support the same events with one exception: the
    ``instance_create`` event.  This event is only available at the
    module-level and not on individual XellgridWidget instances.

    The reason it's not available on individual xellgrid instances is because
    the only time it fires is when a new instance is created. This means
    it's already done firing by the time a user has a chance to hook up any
    event listeners.

    Here's the full list of events that can be listened for via this
    module-level ``on`` method::

        [
            'instance_created',
            'cell_edited',
            'selection_changed',
            'viewport_changed',
            'row_added',
            'row_removed',
            'filter_dropdown_shown',
            'filter_changed',
            'sort_changed',
            'text_filter_viewport_changed',
            'json_updated'
        ]

    See Also
    --------
    XellgridWidget.on :
        Same as this ``on`` method except it listens for events on an
        individual XellgridWidget instance rather than on all instances.  See
        this method for a list of all the types of events that can be
        listened for via either ``on`` method.
    off:
        Unhook a handler that was hooked up using this ``on`` method.

    """
    handlers.on(names, handler)


def off(names, handler):
    """
    Remove a xellgrid event handler that was registered with the ``on`` method.

    Parameters
    ----------
    names : list, str, All (default: All)
        The names of the events for which the specified handler should be
        uninstalled. If names is All, the specified handler is uninstalled
        from the list of notifiers corresponding to all events.
    handler : callable
        A callable that was previously registered with the 'on' method.

    See Also
    --------
    on:
        The method for hooking up handlers that this ``off`` method can remove.
    """
    handlers.off(names, handler)


handlers = EventHandlers()
