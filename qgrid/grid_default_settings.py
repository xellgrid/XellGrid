class _DefaultSettings(object):

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
            'maxVisibleRows': 8,
            'minVisibleRows': 8,
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
        return 6

    @property
    def column_options(self):
        return self._column_options
