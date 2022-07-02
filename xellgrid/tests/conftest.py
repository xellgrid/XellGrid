"""Global test fixtures."""
import pandas as pd
from pytest import fixture
from xellgrid import XellgridWidget

@fixture
def set_test_df():
    test_df = pd.DataFrame(
    {
        "A": 1.0,
        "Date": pd.Timestamp("20130102"),
        "C": pd.Series(1, index=list(range(4)), dtype="float32"),
        "E": pd.Categorical(["test", "train", "foo", "bar"]),
        "F": ["foo", "bar", "buzz", "fox"],
        "D": [1, "bar", "buzz", "fox"]
    })
    return test_df


@fixture
def reset_tabs():
    XellgridWidget.tabs = {}
    yield
    XellgridWidget.tabs = {}

