from ipywidgets import Text
from pytest import raises
from xellgrid.xell_tabs import XellTabs


def test_initialization(reset_tabs):
    with raises(Exception):
        XellTabs()

def test_add_widget(reset_tabs):
    test = Text()
    XellTabs.add_widget('test', test)
    assert test in XellTabs.get_tabs().children


def test_get_widget(reset_tabs):
    test = Text()
    XellTabs.add_widget('test', test)
    test1 = XellTabs.get_widget("test")
    assert test is test1

def test_clear(reset_tabs):
    test = Text()
    XellTabs.add_widget('test', test)
    XellTabs.clear()
    assert len(XellTabs.get_tabs().children) == 0


def test_get_tabs(reset_tabs):
    test = Text()
    XellTabs.add_widget('test', test)
    assert len(XellTabs.get_tabs().children) == 1
    assert XellTabs.get_tabs().get_title(0) == "test"