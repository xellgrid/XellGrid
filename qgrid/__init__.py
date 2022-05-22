from ._version import version_info, __version__  # noqa F401

from .grid import (
    QgridWidget,
    QGridWidget,
)

from .grid_default_settings import (
    set_defaults,
    set_grid_option,
)

from .grid_event_handlers import (
    on,
    off
)

from .grid_display_options import (
    enable,
    disable,
    show_grid,
)


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "qgrid",
            "require": "qgrid/extension",
        }
    ]


__all__ = [
    "enable",
    "disable",
    "set_defaults",
    "on",
    "off",
    "set_grid_option",
    "show_grid",
    "QgridWidget",
    "QGridWidget",
]
