from os import sync
import io
import base64

import ipywidgets as widgets
import logging
import pandas as pd

import numpy as np
import time
import json
import warnings
from copy import deepcopy

from ipywidgets import Tab
from types import FunctionType
from traitlets import (
    Unicode,
    Instance,
    Bool,
    Integer,
    Dict,
    List,
    Tuple,
    Any,
    HasTraits
)

from uuid import uuid4

from xellgrid.xell_tabs import XellTabs

from .common.dataframe_utils import zero_out_dataframe
from .grid_default_settings import defaults
from .grid_event_handlers import EventHandlers, handlers
from .grid_utils import stringify

from xellgrid.grid_row_operations.add_rows import spreadsheet_insert_rows, spreadsheet_duplicate_last_row

# versions of pandas prior to version 0.20.0 don't support the orient='table'
# when calling the 'to_json' function on DataFrames.  to get around this we
# have our own copy of the panda's 0.20.0 implementation that we use for old
# versions of pandas.
# from distutils.version import LooseVersion
# if LooseVersion(pd.__version__) > LooseVersion('0.20.0'):
#    import pandas.io.json as pd_json
# else:
#    from . import pd_json


PAGE_SIZE = 100
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

class DataLayer(HasTraits):
    _df = Instance(pd.DataFrame)
    _df_json = Unicode('', sync=True)
    _primary_key = List()
    _primary_key_display = Dict({})
    _row_styles = Dict({}, sync=True)
    _disable_grouping = Bool(False)
    _columns = Dict({}, sync=True)
    _editable_rows = Dict({}, sync=True)

    _filter_tables = Dict({})

    _sorted_column_cache = Dict({})
    _interval_columns = List([], sync=True)
    _period_columns = List([])
    _string_columns = List([])
    _sort_helper_columns = Dict({})

    _initialized = Bool(False)
    _ignore_df_changed = Bool(False)

    _unfiltered_df = Instance(pd.DataFrame)

    _index_col_name = Unicode('xellgrid_unfiltered_index', sync=True)
    _sort_col_suffix = Unicode('_xellgrid_sort_column')

    _multi_index = Bool(False, sync=True)
    _edited = Bool(False)
    _selected_rows = List([])

    _viewport_range = Tuple(Integer(),
                            Integer(),
                            default_value=(0, 100),
                            sync=True)

    _df_range = Tuple(Integer(), Integer(), default_value=(0, 100), sync=True)

    _row_count = Integer(0, sync=True)
    _sort_field = Any(None, sync=True)
    _sort_ascending = Bool(True, sync=True)
    _handlers = Instance(EventHandlers)

    # part of user input dataframe and df is used for rendering
    df = Instance(pd.DataFrame)

    precision = Integer(6, sync=True)
    grid_options = Dict(sync=True)
    column_options = Dict({})
    column_definitions = Dict({})
    row_edit_callback = Instance(FunctionType, sync=False, allow_none=True)
    show_toolbar = Bool(False, sync=True)
    id = Unicode('', sync=True) 
    title = Unicode('', sync=True)
    
    def __init__(self, core_df=None, *args, **kwargs):
        start_time_init = time.time()
        self.id = kwargs["title"]
        self.title = kwargs["title"]
        self.df = kwargs['df']
        self.widget = kwargs['widget']
        
        self._core_df = core_df
        self._initialized = True
        self._handlers = EventHandlers()

        handlers.notify_listeners({
            'name': 'instance_created'
        }, self)

        start_time_update_render_df = time.time()
        if self.df is not None:
            self._update_render_df()
        end_time_update_render_df = time.time()
        logging.debug("update df took: %s seconds", end_time_update_render_df - start_time_update_render_df)

        end_time_init = time.time()
        logging.debug("Xell grid initiation took: %s seconds", end_time_init - start_time_init)

    def _grid_options_default(self):
        return defaults.grid_options

    def _precision_default(self):
        return defaults.precision

    def _show_toolbar_default(self):
        return defaults.show_toolbar

    def on(self, names, handler):
        """
        Setup a handler to be called when a user interacts with the current
        instance.

        Parameters
        ----------
        names : list, str, All
            If names is All, the handler will apply to all events.  If a list
            of str, handler will apply to all events named in the list.  If a
            str, the handler will apply just the event with that name.
        handler : callable
            A callable that is called when the event occurs. Its
            signature should be ``handler(event, xellgrid_widget)``, where
            ``event`` is a dictionary and ``xellgrid_widget`` is the XellgridWidget
            instance that fired the event. The ``event`` dictionary at least
            holds a ``name`` key which specifies the name of the event that
            occurred.

        Notes
        -----
        Here's the list of events that you can listen to on XellgridWidget
        instances via the ``on`` method::

            [
                'cell_edited',
                'selection_changed',
                'viewport_changed',
                'row_added',
                'row_removed',
                'filter_dropdown_shown',
                'filter_changed',
                'sort_changed',
                'text_filter_viewport_changed',
                'json_updated'
            ]

        The following bullet points describe the events listed above in more
        detail.  Each event bullet point is followed by sub-bullets which
        describe the keys that will be included in the ``event`` dictionary
        for each event.

        * **cell_edited** The user changed the value of a cell in the grid.

            * **index** The index of the row that contains the edited cell.
            * **column** The name of the column that contains the edited cell.
            * **old** The previous value of the cell.
            * **new** The new value of the cell.

        * **filter_changed** The user changed the filter setting for a column.

            * **column** The name of the column for which the filter setting
            was changed.

        * **filter_dropdown_shown** The user showed the filter control for a
        column by clicking the filter icon in the column's header.

            * **column** The name of the column for which the filter control
            was shown.

        * **json_updated** A user action causes XellgridWidget to send rows of
        data (in json format) down to the browser. This happens as a side
        effect of certain actions such as scrolling, sorting, and filtering.

            * **triggered_by** The name of the event that resulted in
            rows of data being sent down to the browser.  Possible values
            are ``change_viewport``, ``change_filter``, ``change_sort``,
            ``add_row``, ``remove_row``, and ``edit_cell``.
            * **range** A tuple specifying the range of rows that have been
            sent down to the browser.

        * **row_added** The user added a new row using the "Add Row" button
        in the grid toolbar.

            * **index** The index of the newly added row.
            * **source** The source of this event.  Possible values are
            ``api`` (an api method call) and ``gui`` (the grid interface).

        * **row_removed** The user added removed one or more rows using the
        "Remove Row" button in the grid toolbar.

            * **indices** The indices of the removed rows, specified as an
            array of integers.
            * **source** The source of this event.  Possible values are
            ``api`` (an api method call) and ``gui`` (the grid interface).

        * **selection_changed** The user changed which rows were highlighted
        in the grid.

            * **old** An array specifying the indices of the previously
            selected rows.
            * **new** The indices of the rows that are now selected, again
            specified as an array.
            * **source** The source of this event.  Possible values are
            ``api`` (an api method call) and ``gui`` (the grid interface).

        * **sort_changed** The user changed the sort setting for the grid.

            * **old** The previous sort setting for the grid, specified as a
            dict with the following keys:

                * **column** The name of the column that the grid was sorted by
                * **ascending** Boolean indicating ascending/descending order

            * **new** The new sort setting for the grid, specified as a dict
            with the following keys:

                * **column** The name of the column that the grid is currently
                sorted by
                * **ascending** Boolean indicating ascending/descending order

        * **text_filter_viewport_changed** The user scrolled the new rows
        into view in the filter dropdown for a text field.

            * **column** The name of the column whose filter dropdown is
            visible
            * **old** A tuple specifying the previous range of visible rows
            in the filter dropdown.
            * **new** A tuple specifying the range of rows that are now
            visible in the filter dropdown.

        * **viewport_changed** The user scrolled the new rows into view in
        the grid.

            * **old** A tuple specifying the previous range of visible rows.
            * **new** A tuple specifying the range of rows that are now
            visible.

        The ``event`` dictionary for every type of event will contain a
        ``name`` key specifying the name of the event that occurred.  That
        key is excluded from the lists of keys above to avoid redundacy.

        See Also
        --------
        on :
            Same as the instance-level ``on`` method except it listens for
            events on all instances rather than on an individual XellgridWidget
            instance.
        XellgridWidget.off:
            Unhook a handler that was hooked up using the instance-level
            ``on`` method.

        """
        self._handlers.on(names, handler)

    def off(self, names, handler):
        """
        Remove a xellgrid event handler that was registered with the current
        instance's ``on`` method.

        Parameters
        ----------
        names : list, str, All (default: All)
            The names of the events for which the specified handler should be
            uninstalled. If names is All, the specified handler is uninstalled
            from the list of notifiers corresponding to all events.
        handler : callable
            A callable that was previously registered with the current
            instance's ``on`` method.

        See Also
        --------
        XellgridWidget.on:
            The method for hooking up instance-level handlers that this
            ``off`` method can remove.

        """
        self._handlers.off(names, handler)

    def _update_render_df(self):
        self._ignore_df_changed = True

        # make a copy of the user's dataframe
        self._df = self.df.copy()
        
        # insert a column which we'll use later to map edits from
        # a filtered version of this df back to the unfiltered version
        self._df.insert(0, self._index_col_name, range(0, len(self._df)))

        # keep an unfiltered version to serve as the starting point
        # for filters, and the state we return to when filters are removed
        # TODO - this is very costly for a large DF, consider just save the original index order

        self._unfiltered_df = self._df.copy()

        update_table(self, update_columns=True, fire_data_change_event=False)
        self._ignore_df_changed = False
        
    def _rebuild_widget(self):
        self._update_render_df()
        self.widget.send({'type': 'draw_table'})

    def _df_changed(self):
        """Build the Data Table for the DataFrame."""
        if self._ignore_df_changed or not self._initialized:
            return
        self._rebuild_widget()

    def _precision_changed(self):
        if not self._initialized:
            return
        self._rebuild_widget()

    def _grid_options_changed(self):
        if not self._initialized:
            return
        self._rebuild_widget()

    def _show_toolbar_changed(self):
        if not self._initialized:
            return
        self.widget.send({'type': 'change_show_toolbar', 'title': self.title})


    def _update_sort(self):
        try:
            if self._sort_field is None:
                return
            self._disable_grouping = False
            if self._sort_field in self._primary_key:
                if len(self._primary_key) == 1:
                    self._df.sort_index(
                        ascending=self._sort_ascending,
                        inplace=True
                    )
                else:
                    level_index = self._primary_key.index(self._sort_field)
                    self._df.sort_index(
                        level=level_index,
                        ascending=self._sort_ascending,
                        inplace=True
                    )
                    if level_index > 0:
                        self._disable_grouping = True
            else:
                self._df.sort_values(
                    self._sort_field,
                    ascending=self._sort_ascending,
                    inplace=True
                )
                self._disable_grouping = True
        except TypeError:
            self.log.info('TypeError occurred, assuming mixed data type '
                        'column')
            # if there's a TypeError, assume it means that we have a mixed
            # type column, and attempt to create a stringified version of
            # the column to use for sorting/filtering
            self._df.sort_values(
                self._initialize_sort_column(self._sort_field),
                ascending=self._sort_ascending,
                inplace=True
            )

    # Add a new column which is a stringified version of the column whose name
    # was passed in, which can be used for sorting and filtering (to avoid
    # error caused by the type of data in the column, like having multiple
    # data types in a single column).
    def _initialize_sort_column(self, col_name, to_timestamp=False):
        sort_column_name = self._sort_helper_columns.get(col_name)
        if sort_column_name:
            return sort_column_name

        sort_col_series = \
            self._get_col_series_from_df(col_name, self._df)
        sort_col_series_unfiltered = \
            self._get_col_series_from_df(col_name, self._unfiltered_df)
        sort_column_name = str(col_name) + self._sort_col_suffix

        if to_timestamp:
            self._df[sort_column_name] = sort_col_series.to_timestamp()
            self._unfiltered_df[sort_column_name] = \
                sort_col_series_unfiltered.to_timestamp()
        else:
            self._df[sort_column_name] = sort_col_series.map(str)
            self._unfiltered_df[sort_column_name] = \
                sort_col_series_unfiltered.map(str)

        self._sort_helper_columns[col_name] = sort_column_name
        return sort_column_name

    def _handle_show_filter_dropdown(self, content):
        col_name = content['field']
        col_info = self._columns[col_name]
        if 'filter_info' in col_info and 'selected' in col_info['filter_info']:
            df_for_unique = self._unfiltered_df
        else:
            df_for_unique = self._df

        # if there's a period index column, add a sort column which has the
        # same values, but converted to timestamps instead of period objects.
        # we'll use that sort column for all subsequent sorts/filters.
        if col_name in self._period_columns:
            self._initialize_sort_column(col_name,
                                        to_timestamp=True)

        col_series = self._get_col_series_from_df(col_name, df_for_unique)
        if 'is_index' in col_info:
            col_series = pd.Series(col_series)

        if col_info['type'] in ['integer', 'number']:
            if 'filter_info' not in col_info or \
                    (col_info['filter_info']['min'] is None and
                    col_info['filter_info']['max'] is None):
                col_info['slider_max'] = max(col_series)
                col_info['slider_min'] = min(col_series)
                self._columns[col_name] = col_info
            self.widget.send({
                'type': 'column_min_max_updated',
                'field': col_name,
                'col_info': col_info,
                'title': self.title
            })
            return
        elif col_info['type'] == 'datetime':
            if 'filter_info' not in col_info or \
                    (col_info['filter_info']['min'] is None and
                    col_info['filter_info']['max'] is None):
                col_info['filter_max'] = max(col_series)
                col_info['filter_min'] = min(col_series)
                self._columns[col_name] = col_info
            self.widget.send({
                'type': 'column_min_max_updated',
                'field': col_name,
                'col_info': col_info,
                'title': self.title
            })
            return
        elif col_info['type'] == 'boolean':
            self.log.info('handling boolean type')
            if 'filter_info' not in col_info:
                values = []
                for possible_val in [True, False]:
                    if possible_val in col_series:
                        values.append(possible_val)
                col_info['values'] = values
                self._columns[col_name] = col_info
            self.widget.send({
                'type': 'column_min_max_updated',
                'field': col_name,
                'col_info': col_info,
                'title': self.title
            })
            self.log.info('handled boolean type')
            return
        else:
            if col_info['type'] == 'any':
                unique_list = col_series.cat.categories
            else:
                if col_name in self._sorted_column_cache:
                    unique_list = self._sorted_column_cache[col_name]
                else:
                    unique = col_series.unique()
                    if len(unique) < 500000:
                        try:
                            unique.sort()
                        except TypeError:
                            sort_col_name = \
                                self._initialize_sort_column(col_name)
                            col_series = df_for_unique[sort_col_name]
                            unique = col_series.unique()
                            unique.sort()
                    unique_list = unique.tolist()
                    self._sorted_column_cache[col_name] = unique_list

            if content['search_val'] is not None:
                unique_list = [
                    k for k in unique_list if
                    content['search_val'].lower() in str(k).lower()
                ]

            # if the filter that we're opening is already active (as indicated
            # by the presence of a 'selected' attribute on the column's
            # filter_info attribute), show the selected rows at the top and
            # specify that they should be checked
            if 'filter_info' in col_info and \
                    'selected' in col_info['filter_info']:
                col_filter_info = col_info['filter_info']
                col_filter_table = self._filter_tables[col_name]

                def get_value_from_filter_table(k):
                    return col_filter_table[k]

                selected_indices = col_filter_info['selected'] or []
                if selected_indices == 'all':
                    excluded_indices = col_filter_info['excluded'] or []
                    excluded_values = list(map(get_value_from_filter_table,
                                            excluded_indices))
                    non_excluded_count = 0
                    for i in range(len(unique_list), 0, -1):
                        unique_val = unique_list[i - 1]
                        if unique_val not in excluded_values:
                            non_excluded_count += 1
                            excluded_values.insert(0, unique_val)
                    col_info['values'] = excluded_values
                    col_info['selected_length'] = non_excluded_count
                elif len(selected_indices) == 0:
                    col_info['selected_length'] = 0
                    col_info['values'] = unique_list
                else:
                    selected_vals = list(map(get_value_from_filter_table,
                                            selected_indices))
                    col_info['selected_length'] = len(selected_vals)

                    in_selected = set(selected_vals)
                    in_unique = set(unique_list)

                    in_unique_but_not_selected = list(in_unique - in_selected)
                    in_unique_but_not_selected.sort()
                    selected_vals.extend(in_unique_but_not_selected)

                    col_info['values'] = selected_vals
            else:
                col_info['selected_length'] = 0
                col_info['values'] = unique_list

            length = len(col_info['values'])

            self._filter_tables[col_name] = list(col_info['values'])

            if col_info['type'] == 'any':
                col_info['value_range'] = (0, length)
            else:
                max_items = PAGE_SIZE * 2
                range_max = length
                if length > max_items:
                    col_info['values'] = col_info['values'][:max_items]
                    range_max = max_items
                col_info['value_range'] = (0, range_max)

            col_info['viewport_range'] = col_info['value_range']
            col_info['length'] = length

            self._columns[col_name] = col_info

            if content['search_val'] is not None:
                message_type = 'update_data_view_filter'
            else:
                message_type = 'column_min_max_updated'
            try:
                self.widget.send({
                    'type': message_type,
                    'field': col_name,
                    'col_info': col_info,
                    'title': self.title
                })
            except ValueError:
                # if there's a ValueError, assume it's because we're
                # attempting to serialize something that can't be converted
                # to json, so convert all the values to strings.
                col_info['values'] = map(str, col_info['values'])
                self.widget.send({
                    'type': message_type,
                    'field': col_name,
                    'col_info': col_info,
                    'title': self.title
                })

    # get any column from a dataframe, including index columns
    def _get_col_series_from_df(self, col_name, df, level_vals=False):
        sort_column_name = self._sort_helper_columns.get(col_name)
        if sort_column_name:
            return df[sort_column_name]

        if col_name in self._primary_key:
            if len(self._primary_key) > 1:
                key_index = self._primary_key.index(col_name)
                if level_vals:
                    return df.index.levels[key_index]

                return df.index.get_level_values(key_index)
            else:
                return df.index
        else:
            return df[col_name]

    def _set_col_series_on_df(self, col_name, df, col_series):
        if col_name in self._primary_key:
            if len(self._primary_key) > 1:
                key_index = self._primary_key.index(col_name)
                prev_name = df.index.levels[key_index].name
                df.index.set_levels(col_series, level=key_index, inplace=True)
                df.index.rename(prev_name, level=key_index, inplace=True)
            else:
                prev_name = df.index.name
                df.set_index(col_series, inplace=True)
                df.index.rename(prev_name)
        else:
            df[col_name] = col_series

    def _append_condition_for_column(self, col_name, filter_info, conditions):
        col_series = self._get_col_series_from_df(col_name,
                                                self._unfiltered_df)
        if filter_info['type'] == 'slider':
            if filter_info['min'] is not None:
                conditions.append(col_series >= filter_info['min'])
            if filter_info['max'] is not None:
                conditions.append(col_series <= filter_info['max'])
        elif filter_info['type'] == 'date':
            if filter_info['min'] is not None:
                conditions.append(
                    col_series >= pd.to_datetime(filter_info['min'], unit='ms')
                )
            if filter_info['max'] is not None:
                conditions.append(
                    col_series <= pd.to_datetime(filter_info['max'], unit='ms')
                )
        elif filter_info['type'] == 'boolean':
            if filter_info['selected'] is not None:
                conditions.append(
                    col_series == filter_info['selected']
                )
        elif filter_info['type'] == 'text':
            if col_name not in self._filter_tables:
                return
            col_filter_table = self._filter_tables[col_name]
            selected_indices = filter_info['selected']
            excluded_indices = filter_info['excluded']

            def get_value_from_filter_table(i):
                return col_filter_table[i]

            if selected_indices == "all":
                if excluded_indices is not None and len(excluded_indices) > 0:
                    excluded_values = list(
                        map(get_value_from_filter_table, excluded_indices)
                    )
                    conditions.append(~col_series.isin(excluded_values))
            elif selected_indices is not None and len(selected_indices) > 0:
                selected_values = list(
                    map(get_value_from_filter_table, selected_indices)
                )
                conditions.append(col_series.isin(selected_values))

    def _handle_change_filter(self, content):
        col_name = content['field']
        columns = self._columns.copy()
        col_info = columns[col_name]
        col_info['filter_info'] = content['filter_info']
        columns[col_name] = col_info

        conditions = []
        for key, value in columns.items():
            if 'filter_info' in value:
                self._append_condition_for_column(
                    key, value['filter_info'], conditions
                )

        self._columns = columns

        self._ignore_df_changed = True
        if len(conditions) == 0:
            self._df = self._unfiltered_df.copy()
        else:
            combined_condition = conditions[0]
            for c in conditions[1:]:
                combined_condition = combined_condition & c

            self._df = self._unfiltered_df[combined_condition].copy()

        if len(self._df) < self._viewport_range[0]:
            viewport_size = self._viewport_range[1] - self._viewport_range[0]
            range_top = max(0, len(self._df) - viewport_size)
            self._viewport_range = (range_top, range_top + viewport_size)

        self._sorted_column_cache = {}
        self._update_sort()
        update_table(self, triggered_by='change_filter')
        self._ignore_df_changed = False

    def _handle_xellgrid_msg(self, widget, content, buffers=None):
        try:
            self._handle_xellgrid_msg_helper(content)
        except Exception as e:
            self.log.error(e)
            self.log.exception("Unhandled exception while handling msg")

    def _handle_xellgrid_msg_helper(self, content):
        """Handle incoming messages from the XellGridView"""
        if 'type' not in content:
            return

        if content['type'] == 'edit_cell':
            col_info = self._columns[content['column']]
            try:
                location = (self._df.index[content['row_index']],
                            content['column'])
                old_value = self._df.loc[location]

                val_to_set = content['value']
                if col_info['type'] == 'datetime':
                    val_to_set = pd.to_datetime(val_to_set)
                    # pandas > 18.0 compat
                    if old_value.tz != val_to_set.tz:
                        val_to_set = val_to_set.tz_convert(tz=old_value.tz)

                self._df.loc[location] = val_to_set

                query = self._unfiltered_df[self._index_col_name] == \
                        content['unfiltered_index']
                self._unfiltered_df.loc[query, content['column']] = val_to_set
                self._notify_listeners({
                    'name': 'cell_edited',
                    'index': location[0],
                    'column': location[1],
                    'old': old_value,
                    'new': val_to_set,
                    'source': 'gui'
                })

            except (ValueError, TypeError):
                msg = "Error occurred while attempting to edit the " \
                    "DataFrame. Check the notebook server logs for more " \
                    "information."
                self.log.exception(msg)
                self.widget.send({
                    'type': 'show_error',
                    'error_msg': msg,
                    'triggered_by': 'add_row',
                    'title': self.title
                })
                return
        elif content['type'] == 'change_selection':
            self._change_selection(content['rows'], 'gui')
        elif content['type'] == 'change_viewport':
            old_viewport_range = self._viewport_range
            self._viewport_range = (content['top'], content['bottom'])

            # if the viewport didn't change, do nothing
            if old_viewport_range == self._viewport_range:
                return

            update_table(self, triggered_by='change_viewport')
            self._notify_listeners({
                'name': 'viewport_changed',
                'old': old_viewport_range,
                'new': self._viewport_range
            })

        elif content['type'] == 'add_row':
            row_index = self._duplicate_last_row()
            self._notify_listeners({
                'name': 'row_added',
                'index': row_index,
                'source': 'gui'
            })
        elif content['type'] == 'add_empty_row':
            row_index = content['row']
            new_index = self._add_empty_row(row_index)
            self._notify_listeners({
                'name': 'row_added',
                'index': new_index,
                'source': 'gui'
            })
        elif content['type'] == 'remove_row':
            removed_indices = self._remove_rows()
            self._notify_listeners({
                'name': 'row_removed',
                'indices': removed_indices,
                'source': 'gui'
            })
        elif content['type'] == 'change_filter_viewport':
            col_name = content['field']
            col_info = self._columns[col_name]
            col_filter_table = self._filter_tables[col_name]

            from_index = max(content['top'] - PAGE_SIZE, 0)
            to_index = max(content['top'] + PAGE_SIZE, 0)

            old_viewport_range = col_info['viewport_range']
            col_info['values'] = col_filter_table[from_index:to_index]
            col_info['value_range'] = (from_index, to_index)
            col_info['viewport_range'] = (content['top'], content['bottom'])

            self._columns[col_name] = col_info
            self.widget.send({
                'type': 'update_data_view_filter',
                'field': col_name,
                'col_info': col_info,
                'title': self.title
            })
            self._notify_listeners({
                'name': 'text_filter_viewport_changed',
                'column': col_name,
                'old': old_viewport_range,
                'new': col_info['viewport_range']
            })
        elif content['type'] == 'change_sort':
            old_column = self._sort_field
            old_ascending = self._sort_ascending
            self._sort_field = content['sort_field']
            self._sort_ascending = content['sort_ascending']
            self._sorted_column_cache = {}
            self._update_sort()
            update_table(self, triggered_by='change_sort')
            self._notify_listeners({
                'name': 'sort_changed',
                'old': {
                    'column': old_column,
                    'ascending': old_ascending
                },
                'new': {
                    'column': self._sort_field,
                    'ascending': self._sort_ascending
                }
            })
        elif content['type'] == 'show_filter_dropdown':
            self._handle_show_filter_dropdown(content)
            self._notify_listeners({
                'name': 'filter_dropdown_shown',
                'column': content['field']
            })
        elif content['type'] == 'change_filter':
            self._handle_change_filter(content)
            self._notify_listeners({
                'name': 'filter_changed',
                'column': content['field']
            })
        elif content['type'] == 'upload_file':
            self._replace_df_by_data(content['data'])

    def _notify_listeners(self, event):
        # notify listeners at the module level
        handlers.notify_listeners(event, self)

        # notify listeners on this class instance
        self._handlers.notify_listeners(event, self)

    def get_changed_df(self):
        """
        Get a copy of the DataFrame that was used to create the current
        instance of XellgridWidget which reflects the current state of the UI.
        This includes any sorting or filtering changes, as well as edits
        that have been made by double clicking cells.

        :rtype: DataFrame
        """
        col_names_to_drop = list(self._sort_helper_columns.values())
        col_names_to_drop.append(self._index_col_name)
        return self._df.drop(col_names_to_drop, axis=1)

    def get_selected_df(self):
        """
        Get a DataFrame which reflects the current state of the UI and only
        includes the currently selected row(s). Internally it calls
        ``get_changed_df()`` and then filters down to the selected rows
        using ``iloc``.

        :rtype: DataFrame
        """
        changed_df = self.get_changed_df()
        return changed_df.iloc[self._selected_rows]

    def get_selected_rows(self):
        """
        Get the currently selected rows.

        :rtype: List of integers
        """
        return self._selected_rows

    def add_row(self, row=None):
        """
        Append a row at the end of the DataFrame.  Values for the new row
        can be provided via the ``row`` argument, which is optional for
        DataFrames that have an integer index, and required otherwise.
        If the ``row`` argument is not provided, the last row will be
        duplicated and the index of the new row will be the index of
        the last row plus one.

        Parameters
        ----------
        row : list (default: None)
            A list of 2-tuples of (column name, column value) that specifies
            the values for the new row.

        See Also
        --------
        XellgridWidget.remove_rows:
            The method for removing a row (or rows).
        """
        if row is None:
            added_index = self._duplicate_last_row()
        else:
            added_index = self._add_row(row)

        self._notify_listeners(
            {"name": "row_added", "index": added_index, "source": "api"}
        )

    def _duplicate_last_row(self):
        """
        Insert a row at the end of the DataFrame by duplicating the
        last row and incrementing the index by 1.
        """
        max_index = max(self._df.index)
        self._df = spreadsheet_duplicate_last_row(self._df)

        # the duplicate record will be concatenated to the unfiltered_df
        self._unfiltered_df = spreadsheet_insert_rows(self._unfiltered_df, self._df.iloc[[max_index]], max_index + 1)
        update_table(self, triggered_by='add_row',
                           scroll_to_row=self._df.index.get_loc(max_index))
        return max_index + 1

    def _add_empty_row(self, row_index):
        """Add empty row into current row_index

        Parameters
        ----------
            row_index (int): current selected row index
        """
        new_row = self._df.iloc[[row_index]]
        new_row = zero_out_dataframe(new_row)
        self._df = spreadsheet_insert_rows(self._df, new_row, row_index + 1)
        self._unfiltered_df = spreadsheet_insert_rows(self._unfiltered_df, new_row, row_index + 1)
        
        update_table(self, triggered_by='add_empty_row',
                           scroll_to_row=self._df.index.get_loc(row_index))

    def _replace_df_by_data(self, data):
        """Replace current dataframe by data

        Parameters
        ----------
            data (dict): data to replace current dataframe
        """
        
        # Decode the base64-encoded string into a binary stream
        binary_data = base64.b64decode(data)

        # Create a BytesIO object from the binary data
        data_stream = io.BytesIO(binary_data)

        df = pd.read_csv(data_stream)
        self._df = df
        self._df.insert(0, self._index_col_name, range(0, len(self._df)))
        self._unfiltered_df = self._df.copy()
        self._sorted_column_cache = {}
        update_table(self, update_columns=True, fire_data_change_event=True)
    
    def _add_row(self, row):
        """
        Append a new row to the end of the DataFrame given a list of 2-tuples
        of (column name, column value). This method will work for DataFrames
        with arbitrary index types.
        """
        df = self._df

        col_names, col_data = zip(*row)
        col_names = list(col_names)
        col_data = list(col_data)
        index_col_val = dict(row)[df.index.name]

        # check that the given column names match what
        # already exists in the dataframe
        required_cols = set(df.columns.values).union({df.index.name}) - {self._index_col_name}
        if set(col_names) != required_cols:
            msg = "Cannot add row -- column names don't match in " \
                "the existing dataframe"
            self.widget.send({
                'type': 'show_error',
                'error_msg': msg,
                'triggered_by': 'add_row',
                'title': self.title
            })
            return

        for i, s in enumerate(col_data):
            if col_names[i] == df.index.name:
                continue

            df.loc[index_col_val, col_names[i]] = s
            self._unfiltered_df.loc[index_col_val, col_names[i]] = s

        update_table(self, triggered_by='add_row',
                           scroll_to_row=df.index.get_loc(index_col_val),
                           fire_data_change_event=True)

        return index_col_val

    def edit_cell(self, index, column, value):
        """
        Edit a cell of the grid, given the index and column of the cell
        to edit, as well as the new value of the cell. Results in a
        ``cell_edited`` event being fired.

        Parameters
        ----------
        index : object
            The index of the row containing the cell that is to be edited.
        column : str
            The name of the column containing the cell that is to be edited.
        value : object
            The new value for the cell.
        """
        old_value = self._df.loc[index, column]
        self._df.loc[index, column] = value
        self._unfiltered_df.loc[index, column] = value
        update_table(self, triggered_by='edit_cell',
                           fire_data_change_event=True)

        self._notify_listeners({
            'name': 'cell_edited',
            'index': index,
            'column': column,
            'old': old_value,
            'new': value,
            'source': 'api'
        })

    def remove_rows(self, rows=None):
        """
        Remove a row (or rows) from the DataFrame.  The indices of the
        rows to remove can be provided via the optional ``rows`` argument.
        If the ``rows`` argument is not provided, the row (or rows) that are
        currently selected in the UI will be removed.

        Parameters
        ----------
        rows : list (default: None)
            A list of indices of the rows to remove from the DataFrame. For
            a multi-indexed DataFrame, each index in the list should be a
            tuple, with each value in each tuple corresponding to a level of
            the MultiIndex.

        See Also
        --------
        XellgridWidget.add_row:
            The method for adding a row.
        XellgridWidget.remove_row:
            Alias for this method.
        """
        row_indices = self._remove_rows(rows=rows)
        self._notify_listeners({
            'name': 'row_removed',
            'indices': row_indices,
            'source': 'api'
        })
        return row_indices

    def remove_row(self, rows=None):
        """
        Alias for ``remove_rows``, which is provided for convenience
        because this was the previous name of that method.
        """
        return self.remove_rows(rows)

    def _remove_rows(self, rows=None):
        if rows is not None:
            selected_names = rows
        else:
            selected_names = \
                list(map(lambda x: self._df.iloc[x].name, self._selected_rows))

        self._df.drop(selected_names, inplace=True)
        self._unfiltered_df.drop(selected_names, inplace=True)
        self._selected_rows = []
        update_table(self, triggered_by='remove_row')
        return selected_names

    def change_selection(self, rows=[]):
        """
        Select a row (or rows) in the UI.  The indices of the
        rows to select are provided via the optional ``rows`` argument.

        Parameters
        ----------
        rows : list (default: [])
            A list of indices of the rows to select. For a multi-indexed
            DataFrame, each index in the list should be a tuple, with each
            value in each tuple corresponding to a level of the MultiIndex.
            The default value of ``[]`` results in the no rows being
            selected (i.e. it clears the selection).
        """
        new_selection = \
            list(map(lambda x: self._df.index.get_loc(x), rows))

        self._change_selection(new_selection, 'api', send_msg_to_js=True)

    def _change_selection(self, rows, source, send_msg_to_js=False):
        old_selection = self._selected_rows
        self._selected_rows = rows

        # if the selection didn't change, just return without firing
        # the event
        if old_selection == self._selected_rows:
            return

        if send_msg_to_js:
            data_to_send = {
                'type': 'change_selection',
                'rows': rows,
                'title': self.title
            }
            self.widget.send(data_to_send)

        self._notify_listeners({
            'name': 'selection_changed',
            'old': old_selection,
            'new': self._selected_rows,
            'source': source
        })

    def toggle_editable(self):
        """
        Change whether the grid is editable or not, without rebuilding
        the entire grid widget.
        """
        self.change_grid_option('editable', not self.grid_options['editable'])

    def change_grid_option(self, option_name, option_value):
        """
        Change a SlickGrid grid option without rebuilding the entire grid
        widget. Not all options are supported at this point so this
        method should be considered experimental.

        Parameters
        ----------
        option_name : str
            The name of the grid option to be changed.
        option_value : str
            The new value for the grid option.
        """
        self.grid_options[option_name] = option_value
        self.widget.send({
            'type': 'change_grid_option',
            'option_name': option_name,
            'option_value': option_value,
            'title': self.title
        })
    
    def to_dict(self, skip=()):
        out_dict = {}
        for key in self.trait_names():
            if key in skip:
                continue
            out_dict[key] = (getattr(self, key))
        return out_dict

@widgets.register()
class XellgridWidget(widgets.DOMWidget):
    """
    The widget class which is instantiated by the ``show_grid`` method. This
    class can be constructed directly but that's not recommended because
    then default options have to be specified explicitly (since default
    options are normally provided by the ``show_grid`` method).

    The constructor for this class takes all the same parameters as
    ``show_grid``, with one exception, which is that the required
    ``data_frame`` parameter is replaced by an optional keyword argument
    called ``df``.

    See Also
    --------
    show_grid : The method that should be used to construct XellgridWidget
                instances, because it provides reasonable defaults for all
                of the XellGrid options.

    Attributes
    ----------
    df : DataFrame
        Get/set the DataFrame that's being displayed by the current instance.
        This DataFrame will NOT reflect any sorting/filtering/editing
        changes that are made via the UI. To get a copy of the DataFrame that
        does reflect sorting/filtering/editing changes, use the
        ``get_changed_df()`` method.
    grid_options : dict
        Get/set the grid options being used by the current instance.
    precision : integer
        Get/set the precision options being used by the current instance.
    show_toolbar : bool
        Get/set the show_toolbar option being used by the current instance.
    column_options : bool
        Get/set the column options being used by the current instance.
    column_definitions : bool
        Get/set the column definitions (column-specific options)
        being used by the current instance.
    tabs : dict
        Get/Set titles for each df, values is the id of the instance of df
    """

    _view_name = Unicode('XellgridView').tag(sync=True)
    _model_name = Unicode('XellgridModel').tag(sync=True)
    _view_module = Unicode('xellgrid').tag(sync=True)
    _model_module = Unicode('xellgrid').tag(sync=True)
    _view_module_version = Unicode('^1.1.3').tag(sync=True)
    _model_module_version = Unicode('^1.1.3').tag(sync=True)
    
    grid_counter = 1
    tabs = Dict({}, sync=True)
    data_layer_object = {}

    def _handle_xellgrid_msg(self, widget, content, buffers=None):
        try:
            data_layer = self.data_layer_object[content['title']]
            data_layer._handle_xellgrid_msg_helper(content)
            tabs = deepcopy(self.tabs)
            tabs[data_layer.title] = data_layer.to_dict(('_unfiltered_df', '_df', 'df', '_handlers', 'row_edit_callback'))
            self.tabs = tabs
        except Exception as e:
            self.log.error(e)
            self.log.exception("Unhandled exception while handling msg")

    def initialize_dfs(self, *args, **kwargs):
        tabs = {}
        for _ in range(3):
            title = str(self.grid_counter)
            data_layer = DataLayer(title=title, widget=self, *args, **kwargs)
            data_layer._initialized = False
            tabs[title] = data_layer.to_dict(('_unfiltered_df', '_df', '_handlers', 'row_edit_callback'))
            self.data_layer_object[title] = data_layer
            self.grid_counter += 1
        self.tabs = tabs

    def __init__(self, *args, **kwargs):
        self.id = str(uuid4())
        super().__init__(*args, **kwargs)
        self.initialize_dfs(*args, **kwargs)
        self.on_msg(self._handle_xellgrid_msg)
        for data_layer in self.data_layer_object.values():
            data_layer._initialized = True 



def update_table(self, update_columns=False, triggered_by=None, scroll_to_row=None, fire_data_change_event=True):
    df = self._df.copy()

    from_index = max(self._viewport_range[0] - PAGE_SIZE, 0)
    to_index = max(self._viewport_range[0] + PAGE_SIZE, 0)
    new_df_range = (from_index, to_index)

    #TODO register all events to an event enum

    if triggered_by == 'viewport_changed' and \
            self._df_range == new_df_range:
        return

    self._df_range = new_df_range

    df = df.iloc[from_index:to_index]

    self._row_count = len(self._df.index)

    if update_columns:
        self._string_columns = list(df.select_dtypes(
            include=[np.dtype('O'), 'category']
        ).columns.values)

        def should_be_stringified(col_series):
            return col_series.dtype == np.dtype('O') or \
                   hasattr(col_series, 'cat') or \
                   isinstance(col_series, pd.PeriodIndex)

        if type(df.index) == pd.MultiIndex:
            self._multi_index = True
            for idx, cur_level in enumerate(df.index.levels):
                if cur_level.name:
                    col_name = cur_level.name
                    self._primary_key_display[col_name] = col_name
                else:
                    col_name = 'level_%s' % idx
                    self._primary_key_display[col_name] = ""
                self._primary_key.append(col_name)
                if should_be_stringified(cur_level):
                    self._string_columns.append(col_name)
        else:
            self._multi_index = False
            if df.index.name:
                col_name = df.index.name
                self._primary_key_display[col_name] = col_name
            else:
                col_name = 'index'
                self._primary_key_display[col_name] = ""
            self._primary_key = [col_name]

            if should_be_stringified(df.index):
                self._string_columns.append(col_name)

    # call map(str) for all columns identified as string columns, in
    # case any are not strings already
    for col_name in self._string_columns:
        sort_column_name = self._sort_helper_columns.get(col_name)
        if sort_column_name:
            series_to_set = df[sort_column_name]
        else:
            series_to_set = self._get_col_series_from_df(
                col_name, df, level_vals=True
            ).map(stringify)
        self._set_col_series_on_df(col_name, df, series_to_set)

    if type(df.index) == pd.MultiIndex and not self._disable_grouping:
        previous_value = None
        row_styles = {}
        row_loc = from_index
        for index, row in df.iterrows():
            row_style = {}
            last_row = row_loc == (len(self._df) - 1)
            prev_idx = row_loc - 1
            for idx, index_val in enumerate(index):
                col_name = self._primary_key[idx]
                if previous_value is None:
                    row_style[col_name] = 'group-top'
                    continue
                elif index_val == previous_value[idx]:
                    if prev_idx < 0:
                        row_style[col_name] = 'group-top'
                        continue
                    if row_styles[prev_idx][col_name] == 'group-top':
                        row_style[col_name] = 'group-middle'
                    elif row_styles[prev_idx][col_name] == 'group-bottom':
                        row_style[col_name] = 'group-top'
                    else:
                        row_style[col_name] = 'group-middle'
                else:
                    if last_row:
                        row_style[col_name] = 'single'
                    else:
                        row_style[col_name] = 'group-top'
                    if prev_idx >= 0:
                        if row_styles[prev_idx][col_name] == \
                                'group-middle':
                            row_styles[prev_idx][col_name] = 'group-bottom'
                        elif row_styles[prev_idx][col_name] == \
                                'group-top':
                            row_styles[prev_idx][col_name] = 'group-single'
            previous_value = index
            row_styles[row_loc] = row_style
            row_loc += 1

        self._row_styles = row_styles
    else:
        self._row_styles = {}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        df_json = df.to_json(
            None, orient="table", date_format="iso", double_precision=self.precision
        )

    if update_columns:
        self._interval_columns = []
        self._sort_helper_columns = {}
        self._period_columns = []

        # parse the schema that we just exported in order to get the
        # column metadata that was generated by 'to_json'
        parsed_json = json.loads(df_json)
        df_schema = parsed_json['schema']

        columns = {}
        for i, cur_column in enumerate(df_schema['fields']):
            col_name = cur_column['name']
            if 'constraints' in cur_column and \
                    isinstance(cur_column['constraints']['enum'][0], dict):
                cur_column['type'] = 'interval'
                self._interval_columns.append(col_name)

            if 'freq' in cur_column and cur_column['type'] == 'periodindex':
                self._period_columns.append(col_name)

            if col_name in self._primary_key:
                cur_column['is_index'] = True
                cur_column['index_display_text'] = \
                    self._primary_key_display[col_name]
                if len(self._primary_key) > 0:
                    cur_column['level'] = self._primary_key.index(col_name)
                level = self._primary_key.index(col_name)
                if level == 0:
                    cur_column['first_index'] = True
                if self._multi_index and \
                        level == (len(self._primary_key) - 1):
                    cur_column['last_index'] = True

            cur_column['position'] = i
            cur_column['field'] = col_name
            cur_column['id'] = col_name
            cur_column['cssClass'] = cur_column['type']

            columns[col_name] = cur_column

            columns[col_name].update(self.column_options)
            if col_name in self.column_definitions.keys():
                columns[col_name].update(self.column_definitions[col_name])

        self._columns = columns

    # special handling for interval columns: convert to a string column
    # and then call 'to_json' again to get a new version of the table
    # json that has interval columns replaced with text columns
    if len(self._interval_columns) > 0:
        for col_name in self._interval_columns:
            col_series = self._get_col_series_from_df(col_name,
                                                      df,
                                                      level_vals=True)
            col_series_as_strings = col_series.map(lambda x: str(x))
            self._set_col_series_on_df(col_name, df,
                                       col_series_as_strings)

    # special handling for period index columns: call to_timestamp to
    # convert the series to a datetime series before displaying
    if len(self._period_columns) > 0:
        for col_name in self._period_columns:
            sort_column_name = self._sort_helper_columns.get(col_name)
            if sort_column_name:
                series_to_set = df[sort_column_name]
            else:
                temp = self._get_col_series_from_df(
                    col_name, df, level_vals=True
                )
                series_to_set = self._get_col_series_from_df(
                    col_name, df, level_vals=True
                ).to_timestamp()
            self._set_col_series_on_df(col_name, df, series_to_set)

    # and then call 'to_json' again to get a new version of the table
    # json that has interval columns replaced with text columns
    if len(self._interval_columns) > 0 or len(self._period_columns) > 0:
        df_json = pd_json.to_json(None, df,
                                  orient='table',
                                  date_format='iso',
                                  double_precision=self.precision)

    self._df_json = df_json

    if self.row_edit_callback is not None:
        editable_rows = {}
        for index, row in df.iterrows():
            editable_rows[int(row[self._index_col_name])] = \
                self.row_edit_callback(row)
        self._editable_rows = editable_rows

    if fire_data_change_event:
        self._notify_listeners({
            'name': 'json_updated',
            'triggered_by': triggered_by,
            'range': self._df_range
        })
        data_to_send = {
            'type': 'update_data_view',
            'columns': self._columns,
            'triggered_by': triggered_by,
            'title': self.title,
            '_df_json': self._df_json,
            '_row_count': self._row_count,
            '_df_range': self._df_range,
            '_columns': self._columns,
            '_index_col_name': self._index_col_name,
        }
        if scroll_to_row:
            data_to_send['scroll_to_row'] = scroll_to_row
        self.widget.send(data_to_send)


# Alias for legacy support, since we changed the capitalization
XellGridWidget = XellgridWidget
