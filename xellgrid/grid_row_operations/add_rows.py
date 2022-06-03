import pandas as pd

"""
Basic construction of adding rows in a spreadsheet
The function will ignore the index of the given dataframe
and perform a fast concat operation

"""


def spreadsheet_insert_rows(df, rows, selected_row_index, ignore_index=True):
    """
    Concat input rows to a dataFrame given a selected location.
    dataframe is assumed to have a default index.
    This method will work for both series or dataframe format as input.


    :param df: the dataframe with current row index that will be concatenated with
    :param rows: rows to be added
    :param selected_row_index: current row index of the dataframe for insertion, the inserted rows will be above the selected row
    :param ignore_index: if re_index is needed
    :return:
    """

    # split the df into 2 sub dataframe based on input selected row

    if selected_row_index == 0:
        df = pd.concat([rows, df], ignore_index=ignore_index)
    elif selected_row_index <= max(df.index):
        df_top_part = df[:selected_row_index]
        df_bottom_part = df[selected_row_index:]
        df_list = [df_top_part, rows, df_bottom_part]
        df = pd.concat(df_list, ignore_index=ignore_index)
    elif selected_row_index > max(df.index):
        df = pd.concat([df, rows], ignore_index=ignore_index)

    return df.reset_index(drop=True)






