import sys

import pandas as pd
from IPython.core.formatters import (DisplayFormatter, FormatterABC,
                                     PlainTextFormatter)
from ipywidgets import Tab
from mock import patch
from pytest import raises
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


def test_show_grid_with_exceptions():
    """Test show_grid with exceptions"""
    test_df = pd.DataFrame(
        {
            "A": 1.0,
            "Date": pd.Timestamp("20130102"),
            "S": pd.Series(1, index=list(range(4)), dtype="float32"),
            "C": pd.Categorical(["test", "train", "foo", "bar"]),
            "L": ["foo", "bar", "buzz", "fox"],
        })

    # test precision type error
    with raises(TypeError):
        precision_str = 'precision'
        show_grid(test_df, precision=precision_str)

    # test grid_option type error
    with raises(TypeError):
        test_grid_options = 'grid_option'
        show_grid(test_df, grid_options=test_grid_options)

    # test dataframe type error
    with raises(TypeError):
        test_df = dict["a":"abc"]
        show_grid(test_df)

def test_show_grid_with_column_option(set_test_df, reset_tabs):
    """test column_options"""
    test_column_options = {
        'editable': False
    }

    test_grid_options = {
        'maxVisibleRows': 100
    }

    # test show_grid options
    
    tabs = show_grid(set_test_df, title="grid1", column_options=test_column_options, grid_options=test_grid_options)
    assert isinstance(tabs, Tab)
    assert tabs.get_title(0) == "grid1"
    children = tabs.children 
    assert children[0].column_options['editable'] is False
    assert children[0].grid_options['maxVisibleRows'] == 100