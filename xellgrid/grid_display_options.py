import pandas as pd

from IPython.display import display
from numbers import Integral
from .grid_default_settings import defaults
from .grid import XellgridWidget


def _display_as_qgrid(data):
    display(show_grid(data))


def enable(dataframe=True, series=True):
    """
    Automatically use qgrid to display all DataFrames and/or Series
    instances in the notebook.

    Parameters
    ----------
    dataframe : bool
        Whether to automatically use qgrid to display DataFrames instances.
    series : bool
        Whether to automatically use qgrid to display Series instances.
    """
    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        raise ImportError('This feature requires IPython 1.0+')

    ip = get_ipython()
    ip_formatter = ip.display_formatter.ipython_display_formatter

    if dataframe:
        ip_formatter.for_type(pd.DataFrame, _display_as_qgrid)
    else:
        ip_formatter.type_printers.pop(pd.DataFrame, None)

    if series:
        ip_formatter.for_type(pd.Series, _display_as_qgrid)
    else:
        ip_formatter.type_printers.pop(pd.Series)


def disable():
    """
    Stop using qgrid to display DataFrames and Series instances in the
    notebook.  This has the same effect as calling ``enable`` with both
    kwargs set to ``False`` (and in fact, that's what this function does
    internally).
    """
    enable(dataframe=False, series=False)


def show_grid(data_frame,
              show_toolbar=None,
              precision=None,
              grid_options=None,
              column_options=None,
              column_definitions=None,
              row_edit_callback=None,
              grid_defaults=None):

    """
    Renders a DataFrame or Series as an interactive XellGrid, represented by
    an instance of the ``QgridWidget`` class.  The ``QgridWidget`` instance
    is constructed using the options passed in to this function.  The
    ``data_frame`` argument to this function is used as the ``df`` kwarg in
    call to the QgridWidget constructor, and the rest of the parameters
    are passed through as is.

    If the ``data_frame`` argument is a Series, it will be converted to a
    DataFrame before being passed in to the QgridWidget constructor as the
    ``df`` kwarg.

    :rtype: QgridWidget

    Parameters
    ----------
    data_frame : DataFrame
        The DataFrame that will be displayed by this instance of
        QgridWidget.
    grid_options : dict
        Options to use when creating the SlickGrid control (i.e. the
        interactive grid).  See the Notes section below for more information
        on the available options, as well as the default options that this
        widget uses.
    precision : integer
        The number of digits of precision to display for floating-point
        values.  If unset, we use the value of
        `pandas.get_option('display.precision')`.
    show_toolbar : bool
        Whether to show a toolbar with options for adding/removing rows.
        Adding/removing rows is an experimental feature which only works
        with DataFrames that have an integer index.
    column_options : dict
        Column options that are to be applied to every column. See the
        Notes section below for more information on the available options,
        as well as the default options that this widget uses.
    column_definitions : dict
        Column options that are to be applied to individual
        columns. The keys of the dict should be the column names, and each
        value should be the column options for a particular column,
        represented as a dict. The available options for each column are the
        same options that are available to be set for all columns via the
        ``column_options`` parameter. See the Notes section below for more
        information on those options.
    row_edit_callback : callable
        A callable that is called to determine whether a particular row
        should be editable or not. Its signature should be
        ``callable(row)``, where ``row`` is a dictionary which contains a
        particular row's values, keyed by column name. The callback should
        return True if the provided row should be editable, and False
        otherwise.


    Notes
    -----
    The following dictionary is used for ``grid_options`` if none are
    provided explicitly::

        {
            # SlickGrid options
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

            # Qgrid options
            'maxVisibleRows': 15,
            'minVisibleRows': 8,
            'sortable': True,
            'filterable': True,
            'highlightSelectedCell': False,
            'highlightSelectedRow': True
        }

    The first group of options are SlickGrid "grid options" which are
    described in the `SlickGrid documentation
    <https://github.com/mleibman/SlickGrid/wiki/Grid-Options>`_.

    The second group of option are options that were added specifically
    for Qgrid and therefore are not documented in the SlickGrid documentation.
    The following bullet points describe these options.

    * **maxVisibleRows** The maximum number of rows that Qgrid will show.
    * **minVisibleRows** The minimum number of rows that Qgrid will show
    * **sortable** Whether the Qgrid instance will allow the user to sort
      columns by clicking the column headers. When this is set to ``False``,
      nothing will happen when users click the column headers.
    * **filterable** Whether the Qgrid instance will allow the user to filter
      the grid. When this is set to ``False`` the filter icons won't be shown
      for any columns.
    * **highlightSelectedCell** If you set this to True, the selected cell
      will be given a light blue border.
    * **highlightSelectedRow** If you set this to False, the light blue
      background that's shown by default for selected rows will be hidden.

    The following dictionary is used for ``column_options`` if none are
    provided explicitly::

        {
            # SlickGrid column options
            'defaultSortAsc': True,
            'maxWidth': None,
            'minWidth': 30,
            'resizable': True,
            'sortable': True,
            'toolTip': "",
            'width': None

            # Qgrid column options
            'editable': True,
        }

    The first group of options are SlickGrid "column options" which are
    described in the `SlickGrid documentation
    <https://github.com/mleibman/SlickGrid/wiki/Column-Options>`_.

    The ``editable`` option was added specifically for Qgrid and therefore is
    not documented in the SlickGrid documentation.  This option specifies
    whether a column should be editable or not.

    See Also
    --------
    set_defaults : Permanently set global defaults for the parameters
                   of ``show_grid``, with the exception of the ``data_frame``
                   and ``column_definitions`` parameters, since those
                   depend on the particular set of data being shown by an
                   instance, and therefore aren't parameters we would want
                   to set for all QgridWidet instances.
    set_grid_option : Permanently set global defaults for individual
                      grid options.  Does so by changing the defaults
                      that the ``show_grid`` method uses for the
                      ``grid_options`` parameter.
    QgridWidget : The widget class that is instantiated and returned by this
                  method.

    """
    if grid_defaults is None:
        grid_defaults = defaults
    if show_toolbar is None:
        show_toolbar = grid_defaults.show_toolbar
    if precision is None:
        precision = grid_defaults.precision
    if not isinstance(precision, Integral):
        raise TypeError("precision must be int, not %s" % type(precision))
    if column_options is None:
        column_options = grid_defaults.column_options
    else:
        options = grid_defaults.column_options.copy()
        options.update(column_options)
        column_options = options
    if grid_options is None:
        grid_options = grid_defaults.grid_options
    else:
        options = grid_defaults.grid_options.copy()
        options.update(grid_options)
        grid_options = options
    if not isinstance(grid_options, dict):
        raise TypeError(
            "grid_options must be dict, not %s" % type(grid_options)
        )

    # if a Series is passed in, convert it to a DataFrame
    if isinstance(data_frame, pd.Series):
        data_frame = pd.DataFrame(data_frame)
    elif not isinstance(data_frame, pd.DataFrame):
        raise TypeError(
            "data_frame must be DataFrame or Series, not %s" % type(data_frame)
        )

    column_definitions = (column_definitions or {})

    # create a visualization for the dataframe
    return XellgridWidget(df=data_frame, precision=precision,
                       grid_options=grid_options,
                       column_options=column_options,
                       column_definitions=column_definitions,
                       row_edit_callback=row_edit_callback,
                       show_toolbar=show_toolbar)