import pandas as pd

class DefaultSettings(object):

    def __init__(self):
        self._grid_options = {
            'fullWidthRows': True,
            'syncColumnCellResize': True,
            'forceFitColumns': True,
            'defaultColumnWidth': 150,
            'rowHeight': 28,
            'enableColumnReorder': False,
            'enableTextSelectionOnCells': True,
            'editable': True,
            'autoEdit': False,
            'explicitInitialization': True,
            'maxVisibleRows': 10,
            'minVisibleRows': 10,
            'sortable': True,
            'filterable': True,
            'highlightSelectedCell': False,
            'highlightSelectedRow': True,
            'boldIndex': True
        }
        self._column_options = {
            'editable': True,
            # the following options are supported by SlickGrid
            'defaultSortAsc': True,
            'maxWidth': None,
            'minWidth': 30,
            'resizable': True,
            'sortable': True,
            'toolTip': "",
            'width': None
        }
        self._show_toolbar = True
        self._precision = None  # Defer to pandas.get_option

    def set_grid_option(self, optname, optvalue):
        self._grid_options[optname] = optvalue

    def set_defaults(self, show_toolbar=None, precision=None,
                     grid_options=None, column_options=None):
        if show_toolbar is not None:
            self._show_toolbar = show_toolbar
        if precision is not None:
            self._precision = precision
        if grid_options is not None:
            self._grid_options = grid_options
        if column_options is not None:
            self._column_options = column_options

    @property
    def show_toolbar(self):
        return self._show_toolbar

    @property
    def grid_options(self):
        return self._grid_options

    @property
    def precision(self):
        return self._precision or pd.get_option('display.precision') - 1

    @property
    def column_options(self):
        return self._column_options


def set_defaults(show_toolbar=None,
                 precision=None,
                 grid_options=None,
                 column_options=None):
    """
     Set the default XellGrid options.  The options that you can set here are the
    same ones that you can pass into ``QgridWidget`` constructor, with the
    exception of the ``df`` option, for which a default value wouldn't be
    particularly useful (since the purpose of qgrid is to display a DataFrame).

    See the documentation for ``QgridWidget`` for more information.

    Notes
    -----
    This function will be useful to you if you find yourself
    setting the same options every time you create a QgridWidget. Calling
    this ``set_defaults`` function once sets the options for the lifetime of
    the kernel, so you won't have to include the same options every time you
    instantiate a ``QgridWidget``.

    See Also
    --------
    QgridWidget :
        The widget whose default behavior is changed by ``set_defaults``.
    """
    defaults.set_defaults(show_toolbar=show_toolbar,
                          precision=precision,
                          grid_options=grid_options,
                          column_options=column_options)


def set_grid_option(optname, optvalue):
    """
    Set the default value for one of the options that gets passed into the
    SlickGrid constructor.

    Parameters
    ----------
    optname : str
        The name of the option to set.
    optvalue : object
        The new value to set.

    Notes
    -----
    The options you can set here are the same ones
    that you can set via the ``grid_options`` parameter of the ``set_defaults``
    or ``show_grid`` functions.  See the `SlickGrid documentation
    <https://github.com/mleibman/SlickGrid/wiki/Grid-Options>`_ for the full
    list of available options.
    """
    defaults.grid_options[optname] = optvalue


defaults = DefaultSettings()
