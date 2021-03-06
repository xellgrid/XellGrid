import pandas as pd
from xellgrid.common.xellgrid_constants import UNFILTERED_COL_INDEX_NAME

"""
Basic construction of adding rows in a spreadsheet
The function will ignore the index of the given dataframe
and perform a fast concat operation

"""


def spreadsheet_insert_rows(df, rows, selected_row_index, ignore_index=True):
    """
    Concat input an arbitrary rows to a dataFrame (re-indexed) given a selected location.
    dataframe is assumed to have a default index.
    This method will work for both series or dataframe format as input.
    Format of rows and dataframe don't need to be the same.

    :param df: the dataframe with current row index that will be concatenated with
    :param rows: rows to be added
    :param selected_row_index: current row index of the dataframe for insertion, the inserted rows will be above the selected row
    :param ignore_index: if re_index is needed
    :return:
    """

    _max_index = max(df.index)
    if selected_row_index == 0:
        df = pd.concat([rows, df], ignore_index=ignore_index)
    elif selected_row_index <= _max_index:
        df_top_part = df[:selected_row_index]
        df_bottom_part = df[selected_row_index:]
        df_list = [df_top_part, rows, df_bottom_part]
        df = pd.concat(df_list, ignore_index=ignore_index)
    elif selected_row_index > _max_index:
        df = pd.concat([df, rows], ignore_index=ignore_index)

    return df.reset_index(drop=True)


def spreadsheet_duplicate_last_row(df, ignore_index=True, unfiltered_index=UNFILTERED_COL_INDEX_NAME):
    """
    duplicate the last row of a dataframe
    :param df:
    :param ignore_index:
    :param unfiltered_index: used to do unfiltered indexing
    :return:
    """

    max_index = max(df.index)
    last_row = df.iloc[[max_index]].copy()
    if unfiltered_index in df.columns:
        last_row[unfiltered_index] = max_index + 1

    return spreadsheet_insert_rows(df, last_row, max_index + 1, ignore_index).reset_index(drop=True)






