from ._version import __version__  # noqa F401

import json
from pathlib import Path

from .grid import (
    XellgridWidget,
    XellGridWidget
)

from .grid_default_settings import (
    set_defaults,
    set_grid_option,
    defaults
)

from .grid_event_handlers import (
    on,
    off,
    EventHandlers,
    handlers
)

from .grid_display_options import (
    add_tab,
    enable,
    disable,
    get_widget,
    show_grid
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

HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]

__all__ = [
    "add_tab",
    "enable",
    "disable",
    "get_widget",
    "set_defaults",
    "on",
    "off",
    "set_grid_option",
    "show_grid",
    "XellgridWidget",
    "XellGridWidget",
    "defaults",
    "EventHandlers",
    "handlers"
]
