"""Module for utils manipulating dataframe"""
import pandas as pd
import numpy as np
def zero_out_dataframe(dataframe: pd.DataFrame):
    """Zero out dataframe but keep the original dtype.
       if no default value for certain type, i.e. Category, 
       then keep the original data.
    """
    dataframe = dataframe.copy()
    for dtype, col in zip(dataframe.dtypes, dataframe.columns):
        if pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
            dataframe[col] = ""
        elif pd.api.types.is_numeric_dtype(dtype):
            dataframe[col] = 0
        elif  pd.api.types.is_bool_dtype(dtype):
            dataframe[col] = False
    return dataframe
