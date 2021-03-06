import pandas as pd
from xellgrid.grid_row_operations.add_rows import spreadsheet_insert_rows, spreadsheet_duplicate_last_row


def set_test_df():
    test_df = pd.DataFrame(
    {
        "A": 1.0,
        "Date": pd.Timestamp("20130102"),
        "C": pd.Series(1, index=list(range(4)), dtype="float32"),
        "E": pd.Categorical(["test", "train", "foo", "bar"]),
        "F": ["foo", "bar", "buzz", "fox"],
    })
    return test_df

def test_spreadsheet_insert_rows():
    """
    test insert rows for a spreadsheet like operation
    :return:
    """
    test_df = set_test_df()
    test_df.reset_index()

    new_row_dict = {
       "baz": 43,
       "bar": "new bar",
       "boo": 58,
       "foo": "new foo"
    }

    # test adding a series at row 0
    new_row_series = pd.Series(data=new_row_dict)
    result_df = spreadsheet_insert_rows(test_df, new_row_series, 0)
    assert result_df.shape == (8, 6)

    # test adding a dataframe at row 2
    new_row_df = pd.DataFrame([[43, '10', 58, 'new_fool']], columns=['A', 'B', 'C', 'E'])
    result_df = spreadsheet_insert_rows(test_df, new_row_df, 2)
    assert result_df.shape == (5, 6)
    assert result_df.at[2, 'A'] == 43

    # test adding a dataframe at last row
    result_df = spreadsheet_insert_rows(test_df, new_row_df, 20)
    assert result_df.shape == (5, 6)
    assert result_df.at[4, 'A'] == 43


def test_duplicate_last_row():
    """
    test duplicate low row
    :return:
    """
    test_df = set_test_df()
    result_df = spreadsheet_duplicate_last_row(test_df)
    assert result_df.shape == (5, 5)
    assert result_df.at[3, 'C'] == result_df.at[4, 'C']

