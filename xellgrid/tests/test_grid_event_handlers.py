from xellgrid import EventHandlers, handlers, on, off


def on_stub():
    pass


def on_foo():
    pass


def test_event_handlers():
    """
    testing EventHandlers
    :return:
    """

    handler = EventHandlers()
    # test handler.on
    handler.on(['on_stub'], on_stub)
    assert(handler.listeners['on_stub'] is not None)

    # test handler.off
    handler.off(['on_stub'], on_stub)
    assert(not handler.listeners['on_stub'])

    handler.on(['on_stub'], on_stub)
    handler.on(['on_foo'], on_foo)
    handler.off(['on_stub'], None)

    assert(handler.listeners.get('on_stub') is None)
    try:
        handler.off(['foo_foo'], None)
    except KeyError:
        assert True


def test_global_handler_off():
    """
    test global handler off
    :return:
    """
    on(['on_stub'], on_stub)
    off(['on_stub'], on_stub)
    assert(not handlers.listeners['on_stub'])
