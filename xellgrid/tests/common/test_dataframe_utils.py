"""Unit test for dataframe_utils module"""
from xellgrid.common.dataframe_utils import zero_out_dataframe


def test_zero_out_dataframe(set_test_df):
    """Test Zero out dataframe"""

    df = zero_out_dataframe(set_test_df.iloc[[1]])
    assert df['A'].squeeze() == 0
    assert df['C'].squeeze() == 0
    assert df['F'].squeeze() == ""
    assert df['D'].squeeze() == ""
    df['E'].equals(set_test_df['E'])
    df['Date'].equals(set_test_df['Date'])
