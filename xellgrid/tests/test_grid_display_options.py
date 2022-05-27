import sys

import pandas as pd

from mock import patch
from IPython.core.formatters import DisplayFormatter, FormatterABC, PlainTextFormatter

from xellgrid import disable, enable, show_grid
from xellgrid.grid_display_options import _display_as_xellgrid


def test_display_as_xellgrid():
    """
    test _display_as_xellgrid
    :return:
    """
    df = pd.DataFrame()
    view = _display_as_xellgrid(df)
    assert(view is None)


def test_enable_disable(monkeypatch):
    """
    test enable and disable
    :return:
    """

    class MockInteractiveShell:
        display_formatter = DisplayFormatter()
        display_formatter.ipython_display_formatter = PlainTextFormatter()

    def mock_get_ipython():
        return MockInteractiveShell()

    # test enable() and disable()
    with patch("IPython.core.getipython.get_ipython", wraps=mock_get_ipython) as mock_ipython:

        enable(True, True)
        enable(False, True)
        enable(True, False)
        enable(False, False)
        disable()
        assert mock_ipython.call_count == 5

    # test ImportError
    try:
        monkeypatch.setitem(sys.modules, 'IPython.core.getipython', None)
        enable(True, True)
    except ImportError:
        assert True


def test_show_grid():
    test_df = pd.DataFrame(
        {
            "A": 1.0,
            "Date": pd.Timestamp("20130102"),
            "S": pd.Series(1, index=list(range(4)), dtype="float32"),
            "C": pd.Categorical(["test", "train", "foo", "bar"]),
            "L": ["foo", "bar", "buzz", "fox"],
        })

    # test precision type error
    try:
        precision_str = 'precision'
        show_grid(test_df, precision=precision_str)
    except TypeError:
        assert True

    # test column_options,

        test_column_options = {
            'editable': False
        }

        test_grid_options = {
            'maxVisibleRows': 100
        }

    # test show_grid options
    grid = show_grid(test_df, column_options=test_column_options, grid_options=test_grid_options)
    assert grid.column_options['editable'] is False
    assert grid.grid_options['maxVisibleRows'] == 100

    # test grid_option type error
    try:
        test_grid_options = 'grid_option'
        show_grid(test_df, grid_options=test_grid_options)
    except TypeError:
        assert True

    # test dataframe type error
    try:
        test_df = dict["a":"abc"]
        show_grid(test_df)
    except TypeError:
        assert True
