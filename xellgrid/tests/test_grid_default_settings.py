from xellgrid import set_grid_option, defaults


def test_default_settings():
    """
    test DefaultSettings
    :return:
    """
    grid_column_options = {
        'editable': False
    }
    defaults.set_defaults(column_options=grid_column_options)
    assert(defaults.column_options['editable'] is False)


def test_set_grid_option():
    """
    test set_grid_option
    :return:
    """
    # test global set_grid_option method
    set_grid_option('rowHeight', 30)
    assert(defaults.grid_options['rowHeight'] == 30)

    # test class set_grid_option method
    defaults.set_grid_option('rowHeight', 35)
    assert(defaults.grid_options['rowHeight'] == 35)
