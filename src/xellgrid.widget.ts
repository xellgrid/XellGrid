import widgets = require('@jupyter-widgets/base');
import _ = require('underscore');
import moment = require('moment');
import $ = require("jquery");
import date_filter = require('./xellgrid.datefilter');
import slider_filter = require('./xellgrid.sliderfilter');
import text_filter = require('./xellgrid.textfilter');
import boolean_filter = require('./xellgrid.booleanfilter');
import editors = require('./xellgrid.editors');

import 'jqueryui';

import 'slickgrid/slick.core';
import 'slickgrid/lib/jquery.event.drag-2.3.0'
import 'slickgrid/plugins/slick.rowselectionmodel'
import 'slickgrid/plugins/slick.checkboxselectcolumn'
import 'slickgrid/plugins/slick.contextmenu'
import 'slickgrid/plugins/slick.contextmenu.css'
import 'slickgrid/slick.dataview'
import 'slickgrid/slick.grid'
import 'slickgrid/slick.editors'
import 'style-loader!slickgrid/slick.grid.css'
import 'style-loader!slickgrid/slick-default-theme.css'
import 'style-loader!jquery-ui-dist/jquery-ui.min.css'
import './xellgrid.css'
import './menu.css'

declare global {
  interface Window {
    $: any,
    jQuery: any,
    slick_grid: any
  }
}
class MainMenu {
  public activated: boolean;
  public settings: any;
  public mask: any;
  public timeOut: any;

  constructor(){
    this.activated = false;

    this.settings = {
      disabledClass: 'disabled',
      submenuClass: 'submenu'
    }

    this.mask = '<div id="menu-top-mask" style="height: 2px; background-color: #fff; z-index:1001;"/>';
    this.timeOut;
  }

  init(p?: any) {
    var activated = false;

    var settings = {
      disabledClass: 'disabled',
      submenuClass: 'submenu'
    }
  
    var mask = '<div id="menu-top-mask" style="height: 2px; background-color: #fff; z-index:1001;"/>';
    var timeOut: any;

    $.extend(settings, p);

    // var $mask = $('#menu-top-mask');

    $('ul.main-menu > li').click(function (event) {
      var target = $(event.target);
      if (target.hasClass(settings.disabledClass) || target.parents().hasClass(settings.disabledClass) || target.hasClass(settings.submenuClass)) {
        return;
      }

      toggleMenuItem($(this));
    });



    $('ul.main-menu > li').mouseenter(function () {
      if (activated && $(this).hasClass('active-menu') == false) {
        toggleMenuItem($(this));
      }
    });

    $('ul.main-menu > li > ul li').mouseenter(function (e) {
      // Hide all other opened submenus in same level of this item
      var $el = $(e.target);
      if ($el.hasClass('separator')) return;
      clearTimeout(timeOut);
      var parent = $el.closest('ul');
      parent.find('ul.active-sub-menu').each(function () {
        if ($(this) != $el)
          $(this).removeClass('active-sub-menu').hide();
      });
      
      // Show submenu of selected item
      if ($el.children().length > 0) {
        timeOut = setTimeout(function () { toggleSubMenu($el) }, 500);
      }
    });

    $('ul.main-menu > li > ul li').each(function () {
      if ($(this).children('ul').length > 0) {
        $(this).addClass(settings.submenuClass);
      }
    });

    $('ul.main-menu li.' + settings.disabledClass).bind('click', function (e) {
      e.preventDefault();
    });

    //#region - Toggle Main Menu Item -

    var toggleMenuItem = function (el: any) {

      // Hide all open submenus
      $('.active-sub-menu').removeClass('active-sub-menu').hide();

      $('#menu-top-mask').remove();

      var submenu = el.find("ul:first");
      var top = parseInt(el.css('padding-bottom').replace("px", ""), 10) + parseInt(el.css('padding-top').replace("px", ""), 10) +
          el.position().top +
          el.height();

      submenu.prepend($(mask));
      var $mask = $('#menu-top-mask');
      var maskWidth = el.width() +
          parseInt(el.css('padding-left').replace("px", ""), -5) +
          parseInt(el.css('padding-right').replace("px", ""), -5);

      $mask.css({ position: 'absolute',
        top: '-1px',
        width: (maskWidth) + 'px'
      });

      submenu.css({
        position: 'absolute',
        top: top + 'px',
        left: el.position().left + 'px',
        zIndex: 100
      });

      submenu.stop().toggle();
      activated = submenu.is(":hidden") == false;

      !activated ? el.removeClass('active-menu') : el.addClass('active-menu');

      if (activated) {
        $('.active-menu').each(function () {
          if ($(this).offset()!.left != el.offset().left) {
            $(this).removeClass('active-menu');
            $(this).find("ul:first").hide();
          }
        });
      }
    }

    //#endregion

    //#region - Toggle Sub Menu Item -

    var toggleSubMenu = function (el: any) {

      if (el.hasClass(settings.disabledClass)) {
        return;
      }

      var submenu = el.find("ul:first");
      var paddingLeft = parseInt(el.css('padding-right').replace('px', ''), 10);
      var borderTop = parseInt(el.css('border-top-width').replace("px", ""), 10);
      borderTop = !isNaN(borderTop) ? borderTop : 1;
      var top = el.position().top - borderTop;

      submenu.css({
        position: 'absolute',
        top: top + 'px',
        left: el.width() + paddingLeft + 'px',
        zIndex: 1000
      });

      submenu.addClass('active-sub-menu');

      submenu.show();

      el.mouseleave(function () {
        submenu.hide();
      });
    }

    //#endregion

    var closeMainMenu = function () {
      activated = false;
      $('.active-menu').find("ul:first").hide();
      $('.active-menu').removeClass('active-menu');
      $('.active-sub-menu').hide();
    };

    $(document).keyup(function (e) {
      if (e.keyCode == 27) {
        closeMainMenu();
      }
    });

    $(document).bind('click', function (event) {
      var target = $(event.target);
      if (!target.hasClass('active-menu') && !target.parents().hasClass('active-menu')) {
        closeMainMenu();
      }
    });
  }
}


// Model for the xellgrid widget
export class XellgridModel extends widgets.DOMWidgetModel {
  defaults() {
    return _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
      _model_name : 'XellgridModel',
      _view_name : 'XellgridView',
      _model_module : 'xellgrid',
      _view_module : 'xellgrid',
      _model_module_version : '^1.1.3',
      _view_module_version : '^1.1.3',
      _df_json: '',
      _columns: {}
    });
  }
}


// View for the xellgrid widget
export class XellgridView extends widgets.DOMWidgetView {
	public model: any;
	public $el: any;
	public toolbar: any;
	public window_dropdown_menu: any;
	public send: any;
	public grid_elem: any;
	public data_view: any;
	public grid_options: any;
	public index_col_name: any;
	public row_styles: any;
	public columns: any;
	public index_columns: any;
	public filters: any;
	public filter_list: any;
	public date_formats: any;
	public last_vp: any;
	public sort_in_progress: any;
	public sort_indicator: any;
	public resizing_column: any;
	public ignore_selection_changed: any;
	public vp_response_expected: any;
	public next_viewport_msg: any;
	public type_infos: any;
	public loadValue: any;
	public date_value: any;
	public input: any;
	public isValueChanged: any;
	public serializeValue: any;
	public slick_grid: any;
	public grid_header: any;
	public sorted_column: any;
	public sort_ascending: any;
	public viewport_timeout: any;
	public resize_handles: any;
	public df_range: any;
	public df_length: any;
	public buttons: any;
	public update_timeout: any;
	public multi_index: any;
	public in_progress_btn: any;
  public main_menu: any;
  render() {
    // subscribe to incoming messages from the QGridWidget
    this.model.on('msg:custom', this.handle_msg, this);
    this.initialize_qgrid();
  }

  /**
   * Main entry point for drawing the widget,
   * including toolbar buttons if necessary.
   */
  initialize_qgrid() {
    this.$el.empty();
    if (!this.$el.hasClass('xell-grid-container')){
      this.$el.addClass('xell-grid-container');
    }
    this.initialize_toolbar();
    this.initialize_slick_grid();
  }

  initialize_toolbar() {
    if (!this.model.get('show_toolbar')){
      this.$el.removeClass('show-toolbar');
    } else {
      this.$el.addClass('show-toolbar');
    }

    if (this.toolbar){
      return;
    }

    this.toolbar = $("<div class='xell-grid-toolbar'>").appendTo(this.$el);

    this.window_dropdown_menu = $(`
    <div id="menu-bar" > 
    <h1 style="text-align:center;color:#89CFF0;font-size:18px"> XellGrid </h1>
  <ul class="main-menu">
    <li id="menu-file"> File
      <ul>
        <li id="new_dataframe" value="new_value"> New DataFrame 
        </li>
        <li class="separator"></li>
        <li class="icon save" value="save_dataframe"><a href="#">Save<span>Ctrl+S</span></a></li>
        <li class="separator"></li>
        <li class="disabled" value="open_dataframe"><a href="#">Open</a></li>
        <li class="separator"></li>
        <li class="icon print" value="save_code"><a href="#">Save Code<span>Ctrl+P</span></a></li>
      </ul>
    </li>
    <li> Edit
      <ul>
        <li value="add_row">Duplicate Last Row</li>
        <li value="add_empty_row">Create Empty Row</li>
        <li class="separator"></li>
        <li value="remove_row">Remove Row</li>
        <li value="clear_history">Clear Edit History</li>
      </ul>
    </li>
    <li> Sort/Filter
      <ul>
        <li value="filter_history"> Filter History</li>
        <li value="reset_filters"> Reset Filters</li>
        <li class="separator"></li>
        <li value="reset_sort"> Reset Sort</li>
      </ul>
    </li>
    <li> Help
      <ul>
        <li>Tips</li>
      </ul>
    </li>
  </ul>
  <!-- end mainmenu --> 
</div>
    
    `);

    this.window_dropdown_menu.appendTo(this.toolbar);



   this.bind_toolbar_events();
  }

  bind_toolbar_events(message?: any) {
    var that = this
    let activated = false
    // this will find the element with class = main-menu
    this.window_dropdown_menu.main_menu_bar = this.window_dropdown_menu.find('ul.main-menu');
    this.window_dropdown_menu.main_menu_bar.mouseenter((e: any) =>{
      if(activated === false)
      {
        that.main_menu = new MainMenu();
        that.main_menu.init();
        activated = true
      }
    });

    
    $('ul.main-menu > li > ul li').click(function (event) {

      // Prevent click event to propagate to parent elements
      event.stopPropagation();

      // Prevent any operations if item is disabled
      if ($(this).hasClass(that.main_menu.settings.disabledClass)) {
        return;
      }

      // If item is active, check if there are submenus (ul elements inside current li)
      if ($(this).has( "ul" ).length > 0) {
        // Automatically toggle submenu, if any
        that.main_menu.toggleSubMenu($(this));
      }
      else{
        // If there are no submenus, close main menu.
        that.main_menu.closeMainMenu();
      }
    });



    this.window_dropdown_menu.main_menu_bar.click((event: any) => {
      let target = $(event.target);
      if (!target.hasClass('active-menu') && !target.parents().hasClass('active-menu')) {
        this.send({'type': event.target.getAttribute("value")})
      }
    });


  }

  /**
   * Create the grid portion of the widget, which is an instance of
   * SlickGrid, plus automatically created filter controls based on the
   * type of data in the columns of the DataFrame provided by the user.
   */
  initialize_slick_grid() {

    if (!this.grid_elem) {
      this.grid_elem = $("<div class='xell-grid'>").appendTo(this.$el);
    }

    // create the table
    var df_json = JSON.parse(this.model.get('_df_json'));
    var columns = this.model.get('_columns');
    this.data_view = this.create_data_view(df_json.data);
    this.grid_options = this.model.get('grid_options');
    this.index_col_name = this.model.get("_index_col_name");
    this.row_styles = this.model.get("_row_styles");

    this.columns = [];
    this.index_columns = [];
    this.filters = {};
    this.filter_list = [];
    this.date_formats = {};
    this.last_vp = null;
    this.sort_in_progress = false;
    this.sort_indicator = null;
    this.resizing_column = false;
    this.ignore_selection_changed = false;
    this.vp_response_expected = false;
    this.next_viewport_msg = null;

    var number_type_info = {
      filter: slider_filter.SliderFilter,
      validator: editors.validateNumber,
      formatter: this.format_number
    };

    var self = this;
    
    this.type_infos = {
      integer: Object.assign(
        { editor: Slick.Editors.Integer },
        number_type_info
      ),
      number: Object.assign(
        { editor: Slick.Editors.Float },
        number_type_info
      ),
      string: {
        filter: text_filter.TextFilter,
        editor: Slick.Editors.Text,
        formatter: this.format_string
      },
      datetime: {
        filter: date_filter.DateFilter,
        editor: class DateEditor extends Slick.Editors.Date<any> {
          public date_value: any
          public input: any
          public serializeValue: any
          constructor(args: any) {
            super(args);

            this.loadValue = (item) => {
              this.date_value = item[args.column.field];
              var formatted_val = self.format_date(
                  this.date_value, args.column.field
              );
              this.input = $(args.container).find('.editor-text');
              this.input.val(formatted_val);
              this.input[0].defaultValue = formatted_val;
              this.input.select();
              this.input.on("keydown.nav", function (e: any) {
                if (e.keyCode === $.ui.keyCode.LEFT || e.keyCode === $.ui.keyCode.RIGHT) {
                  e.stopImmediatePropagation();
                }
              });
            };

            this.isValueChanged = () => {
              return this.input.val() != this.date_value;
            };

            this.serializeValue = () => {
              if (this.input.val() === "") {
                  return null;
              }
              var parsed_date = moment.parseZone(
                  this.input.val(), "YYYY-MM-DD HH:mm:ss.SSS"
              );
              return parsed_date.format("YYYY-MM-DDTHH:mm:ss.SSSZ");
            };
          }
        },
        formatter: (row: any, cell: any, value: any, columnDef: any, dataContext: any) => {
          if (value === null){
            return "NaT";
          }
          return this.format_date(value, columnDef.name);
        }
      },
      any: {
        filter: text_filter.TextFilter,
        editor: editors.SelectEditor,
        formatter: this.format_string
      },
      interval: {
        formatter: this.format_string
      },
      boolean: {
        filter: boolean_filter.BooleanFilter,
        editor: Slick.Editors.Checkbox,
        formatter: (row: any, cell: any, value: any, columngDef: any, dataContext: any) => {
          return value ? `<span class="fa fa-check"/>` : "";
        }
      }
    };

    $.datepicker.setDefaults({
      gotoCurrent: true,
      dateFormat: 'yyyy-mm-dd',
      constrainInput: false,
      "prevText": "",
      "nextText": ""
    });

    var sorted_columns = Object.values(columns).sort(
        (a: any, b: any) => a.position - b.position
    );
    let cur_column: any 
    for( cur_column of sorted_columns){
      if (cur_column.name == this.index_col_name){
        continue;
      }

      var type_info = this.type_infos[cur_column.type] || {};

      var slick_column = cur_column;

      Object.assign(slick_column, type_info);

      if (cur_column.type == 'any'){
        slick_column.editorOptions = {
          options: cur_column.constraints.enum
        };
      }

      if (slick_column.filter) {
        var cur_filter = new slick_column.filter(
            slick_column.field,
            cur_column.type,
            this
        );
        this.filters[slick_column.id] = cur_filter;
        this.filter_list.push(cur_filter);
      }

      if (cur_column.width == null){
        delete slick_column.width;
      }

      if (cur_column.maxWidth == null){
        delete slick_column.maxWidth;
      }

      // don't allow editing index columns
      if (cur_column.is_index) {
        slick_column.editor = editors.IndexEditor;
        
        if (cur_column.first_index){
          slick_column.cssClass += ' first-idx-col';
        }
        if (cur_column.last_index){
          slick_column.cssClass += ' last-idx-col';
        }

        slick_column.name = cur_column.index_display_text;
        slick_column.level = cur_column.level;

        if (this.grid_options.boldIndex) {
            slick_column.cssClass += ' idx-col';
        }

        this.index_columns.push(slick_column);
        continue;
      }

      if (cur_column.editable == false) {
        slick_column.editor = null;
      }

      this.columns.push(slick_column);
    }

    if (this.index_columns.length > 0) {
      this.columns = this.index_columns.concat(this.columns);
    }

    // var row_count = 0;

    // set window.slick_grid for easy troubleshooting in the js console
    window.slick_grid = this.slick_grid = new Slick.Grid(
      this.grid_elem,
      this.data_view,
      this.columns,
      this.grid_options
    );
    this.grid_elem.data('slickgrid', this.slick_grid);

    if (this.grid_options.forceFitColumns){
      this.grid_elem.addClass('force-fit-columns');
    }

    if (this.grid_options.highlightSelectedCell) {
      this.grid_elem.addClass('highlight-selected-cell');
    }

    // compare to false since we still want to show row
    // selection if this option is excluded entirely
    if (this.grid_options.highlightSelectedRow != false) {
      this.grid_elem.addClass('highlight-selected-row');
    }

    setTimeout(() => {
      this.slick_grid.init();
      this.update_size();
    }, 1);

    this.slick_grid.setSelectionModel(new Slick.RowSelectionModel());
    this.slick_grid.setCellCssStyles("grouping", this.row_styles);
    this.slick_grid.render();
    
    this.update_size();

    var render_header_cell = (e: any, args: any) => {
      var cur_filter = this.filters[args.column.id];
        if (cur_filter) {
          cur_filter.render_filter_button($(args.node), this.slick_grid);
        }
    };

    if (this.grid_options.filterable != false) {
      this.slick_grid.onHeaderCellRendered.subscribe(render_header_cell);
    }

    // Force the grid to re-render the column headers so the
    // onHeaderCellRendered event is triggered.
    this.slick_grid.setColumns(this.slick_grid.getColumns());

    $(window).resize(() => {
      this.slick_grid.resizeCanvas();
    });

    this.slick_grid.setSortColumns([]);

    this.grid_header = this.$el.find('.slick-header-columns');
    var handle_header_click = (e: any) => {
      if (this.resizing_column) {
        return;
      }

      if (this.sort_in_progress){
        return;
      }

      var col_header = $(e.target).closest(".slick-header-column");
      if (!col_header.length) {
        return;
      }

      var column = col_header.data("column");
      if (column.sortable == false){
        return;
      }

      this.sort_in_progress = true;

      if (this.sorted_column == column){
        this.sort_ascending = !this.sort_ascending;
      } else {
        this.sorted_column = column;
        if ('defaultSortAsc' in column) {
          this.sort_ascending = column.defaultSortAsc;
        } else{
          this.sort_ascending = true;
        }
      }

      var all_classes = 'fa-sort-asc fa-sort-desc fa fa-spin fa-spinner';
      var clicked_column_sort_indicator = col_header.find('.slick-sort-indicator');
      if (clicked_column_sort_indicator.length == 0){
        clicked_column_sort_indicator =
            $("<span class='slick-sort-indicator'/>").appendTo(col_header);
      }

      this.sort_indicator = clicked_column_sort_indicator;
      this.sort_indicator.removeClass(all_classes);
      this.grid_elem.find('.slick-sort-indicator').removeClass(all_classes);
      this.sort_indicator.addClass(`fa fa-spinner fa-spin`);
      var msg = {
        'type': 'change_sort',
        'sort_field': this.sorted_column.field,
        'sort_ascending': this.sort_ascending
      };
      this.send(msg);
    };

    if (this.grid_options.sortable != false) {
      this.grid_header.click(handle_header_click)
    }

    var contextMenuOptions = {
      // optionally and conditionally define when the the menu is usable,
      // this should be used with a custom formatter to show/hide/disable the menu
      commandTitle: "Commands",
      // which column to show the command list? when not defined it will be shown over all columns
      commandItems: [
        { command: "remove_row", title: "Delete A Row",
          action: (e: any, args: any) => {
            this.send({'type': "remove_row"})
          }
        },
        { command: "add_empty_row", title: "Add An Empty Row", iconImage: "", cssClass: "bold", textCssClass: "red",
          action: (e: any, args: any) => {
            this.send({
              'type': "add_empty_row",
              'row': args.row,
              'cell': args.cell
            })
          }
        },
        { 
          command: "add_row", title: "Duplicate Last Row", iconImage: "", cssClass: "bold", textCssClass: "red",
          action: (e: any, args: any) => {
            this.send({'type': "add_row"})
          }
        },
        // { divider: true },
        // {
        //   command: "help", title: "Help", iconCssClass: "icon-help"
        // }
      ],

      // Options allows you to edit a column from an option chose a list
      // for example, changing the Priority value
      // you can also optionally define an array of column ids that you wish to display this option list (when not defined it will show over all columns)
      optionTitle: "Change Priority",
      optionShownOverColumnIds: ["priority"], // optional, when defined it will only show over the columns (column id) defined in the array
      optionItems: [
        {
          option: 0, title: "none", textCssClass: "italic",
          // only enable this option when there's no Effort Driven
          itemUsabilityOverride: function (args: any) {
          },
          // you can use the "action" callback and/or subscribe to the "onCallback" event, they both have the same arguments
          action: function (e: any, args: any) {
            // action callback.. do something
          },
        },
        { option: 1, iconImage: "../images/info.gif", title: "Low" },
        { option: 2, iconImage: "../images/info.gif", title: "Medium" },
        { option: 3, iconImage: "../images/bullet_star.png", title: "High" },
        // you can pass divider as a string or an object with a boolean
        // "divider",
        { divider: true },
        {
          option: 4, title: "Extreme", disabled: true,
          // only shown when there's no Effort Driven
          itemVisibilityOverride: function (args: any) {
          }
        },
      ]
    };

    let contextMenuPlugin = new (Slick as any).Plugins.ContextMenu(contextMenuOptions);
    this.slick_grid.registerPlugin(contextMenuPlugin);
    contextMenuPlugin.onBeforeMenuShow.subscribe((e: any, args: any) =>{
      e.preventDefault();
      e.stopPropagation();
      // for example, you could select the row it was clicked with
      this.slick_grid.setSelectedRows([args.row], e.target); // select the entire row
      //this.slick_grid.setActiveCell(args.row, args.cell, false); // select the cell that the click originated
      console.log("Before the global Context Menu is shown", args);
    });
    contextMenuPlugin.onBeforeMenuClose.subscribe(function (e: any, args: any) {
      console.log("Global Context Menu is closing", args);
    });

    contextMenuPlugin.onAfterMenuShow.subscribe(function (e: any, args: any) {
      // for example, you could select the row it was clicked with
      // grid.setSelectedRows([args.row]); // select the entire row
      //this.slick_grid.setActiveCell(args.row, args.cell, false); // select the cell that the click originated
      console.log("After the Context Menu is shown", args);
    });



    this.slick_grid.onViewportChanged.subscribe((e: any) => {
      if (this.viewport_timeout){
        clearTimeout(this.viewport_timeout);
      }
      this.viewport_timeout = setTimeout(() => {
        this.last_vp = this.slick_grid.getViewport();
        var cur_range = this.model.get('_viewport_range');

        if (this.last_vp.top != cur_range[0] || this.last_vp.bottom != cur_range[1]) {
          var msg = {
            'type': 'change_viewport',
            'top': this.last_vp.top,
            'bottom': this.last_vp.bottom
          };
          if (this.vp_response_expected){
            this.next_viewport_msg = msg
          } else {
            this.vp_response_expected = true;
            this.send(msg);
          }
        }
        this.viewport_timeout = null;
      }, 100);
    });

    // set up callbacks
    let editable_rows = this.model.get('_editable_rows');
    if (editable_rows && Object.keys(editable_rows).length > 0) {
      this.slick_grid.onBeforeEditCell.subscribe((e: any, args: any) => {
        editable_rows = this.model.get('_editable_rows');
        return editable_rows[args.item[this.index_col_name]]
      });
    }

    this.slick_grid.onCellChange.subscribe((e: any, args: any) => {
      var column = this.columns[args.cell].name;
      var data_item = this.slick_grid.getDataItem(args.row);
      var msg = {'row_index': data_item.row_index, 'column': column,
                 'unfiltered_index': data_item[this.index_col_name],
                 'value': args.item[column], 'type': 'edit_cell'};
      this.send(msg);
    });

    this.slick_grid.onSelectedRowsChanged.subscribe((e: any, args: any) => {
      if (!this.ignore_selection_changed) {
        var msg = {'rows': args.rows, 'type': 'change_selection'};
        this.send(msg);
      }
    });

    setTimeout(() => {
      this.$el.closest('.output_wrapper')
          .find('.out_prompt_overlay,.output_collapsed').click(() => {
        setTimeout(() => {
          this.slick_grid.resizeCanvas();
        }, 1);
      });

      this.resize_handles = this.grid_header.find('.slick-resizable-handle');
      this.resize_handles.mousedown((e: any) => {
        this.resizing_column = true;
      });
      $(document).mouseup(() => {
        // wait for the column header click handler to run before
        // setting the resizing_column flag back to false
        setTimeout(() => {
          this.resizing_column = false;
        }, 1);
      });
    }, 1);
  }

  processPhosphorMessage(msg: any) {
    super.processPhosphorMessage(msg)
    switch (msg.type) {
    case 'resize':
    case 'after-show':
      if (this.slick_grid){
        this.slick_grid.resizeCanvas();
      }
      break;
    }
  }

  has_active_filter() {
    for (var i=0; i < this.filter_list.length; i++){
      var cur_filter = this.filter_list[i];
      if (cur_filter.is_active()){
        return true;
      }
    }
    return false;
  }

  /**
   * Main entry point for drawing the widget,
   * including toolbar buttons if necessary.
   */
  create_data_view(df: any) {
    let df_range = this.df_range = this.model.get("_df_range");
    let df_length = this.df_length = this.model.get("_row_count");
    return {
      getLength: () => {
        return df_length;
      },
      getItem: (i: any) => {
        if (i >= df_range[0] && i < df_range[1]){
          var row = df[i - df_range[0]] || {};
          row.row_index = i;
          return row;
        } else {
          return { row_index: i };
        }
      }
    };
  }

  set_data_view(data_view: any) {
    this.data_view = data_view;
    this.slick_grid.setData(data_view);
  }

  format_date(date_string: any, col_name: any) {
    if (!date_string) {
      return "";
    }
    var parsed_date = moment.parseZone(date_string, "YYYY-MM-DDTHH:mm:ss.SSSZ");
    var date_format: string | undefined = undefined;
    if (parsed_date.millisecond() != 0){
       date_format = `YYYY-MM-DD HH:mm:ss.SSS`;
    } else if (parsed_date.second() != 0){
      date_format = "YYYY-MM-DD HH:mm:ss";
    } else if (parsed_date.hour() != 0 || parsed_date.minute() != 0) {
      date_format = "YYYY-MM-DD HH:mm";
    } else {
      date_format = "YYYY-MM-DD";
    }

    if (col_name in this.date_formats){
      var old_format = this.date_formats[col_name];
      if (date_format.length > old_format.length){
        this.date_formats[col_name] = date_format;
        setTimeout(() => {
          this.slick_grid.invalidateAllRows();
          this.slick_grid.render();
        }, 1);
      } else {
        date_format = this.date_formats[col_name];
      }
    } else {
      this.date_formats[col_name] = date_format;
    }

    return parsed_date.format(date_format);
  }

  format_string(row: any, cell: any, value: any, columnDef: any, dataContext: any) {
    return value;
  }

  format_number(row: any, cell: any, value: any, columnDef: any, dataContext: any) {
    if (value === null){
      return 'NaN';
    }
    return value;
  }

  /**
   * Handle messages from the QGridWidget.
   */
  handle_msg(msg: any) {
    if (msg.type === 'draw_table') {
      this.initialize_slick_grid();
    } else if (msg.type == 'show_error') {
      alert(msg.error_msg);
      if (msg.triggered_by == 'add_row' ||
        msg.triggered_by == 'remove_row'){
        this.reset_in_progress_button();
      }
    } else if (msg.type == 'update_data_view') {
      if (this.buttons) {
        if (this.has_active_filter()) {
          this.buttons.addClass('disabled');
          this.buttons.tooltip('enable');
        } else if (this.buttons.hasClass('disabled')) {
          this.buttons.removeClass('disabled');
          this.buttons.tooltip('disable');
        }
      }
      if (this.update_timeout) {
        clearTimeout(this.update_timeout);
      }
      this.update_timeout = setTimeout(() => {
        var df_json = JSON.parse(this.model.get('_df_json'));
        this.row_styles = this.model.get("_row_styles");
        this.multi_index = this.model.get("_multi_index");
        var data_view = this.create_data_view(df_json.data);

        if (msg.triggered_by === 'change_viewport') {
          if (this.next_viewport_msg) {
            this.send(this.next_viewport_msg);
            this.next_viewport_msg = null;
            return;
          } else {
            this.vp_response_expected = false;
          }
        }

        if (msg.triggered_by == 'change_sort' && this.sort_indicator) {
          var asc = this.model.get('_sort_ascending');
          this.sort_indicator.removeClass(
              'fa-spinner fa-spin fa-sort-asc fa-sort-desc'
          );
          var fa_class = asc ? 'fa-sort-asc' : 'fa-sort-desc';
          this.sort_indicator.addClass(fa_class);
          this.sort_in_progress = false;
        }

        let top_row = null;
        if (msg.triggered_by === 'remove_row') {
          top_row = this.slick_grid.getViewport().top;
        }

        this.set_data_view(data_view);

        var skip_grouping = false;
        if (this.multi_index) {
          for (var i = 1; i < this.filter_list.length; i++) {
            var cur_filter = this.filter_list[i];
            if (cur_filter.is_active()) {
              skip_grouping = true;
            }
          }
        }

        if (skip_grouping) {
          this.slick_grid.removeCellCssStyles("grouping");
        } else {
          this.slick_grid.setCellCssStyles("grouping", this.row_styles);
        }

        this.slick_grid.render();

        if ((msg.triggered_by == 'add_row' ||
            msg.triggered_by == 'remove_row') && !this.has_active_filter()) {
          this.update_size();
        }
        this.update_timeout = null;
        this.reset_in_progress_button();
        if (top_row) {
          this.slick_grid.scrollRowIntoView(top_row);
        } else if (msg.triggered_by === 'add_row') {
          this.slick_grid.scrollRowIntoView(msg.scroll_to_row);
          this.slick_grid.setSelectedRows([msg.scroll_to_row]);
        } else if (msg.triggered_by === 'change_viewport' &&
            this.last_vp.bottom >= this.df_length) {
          this.slick_grid.scrollRowIntoView(this.last_vp.bottom);
        }

        var selected_rows = this.slick_grid.getSelectedRows().filter((row: any) => {
          return row < Math.min(this.df_length, this.df_range[1]);
        });
        this.send({
          'rows': selected_rows,
          'type': 'change_selection'
        });
      }, 100);
    } else if (msg.type == 'change_grid_option') {
      var opt_name = msg.option_name;
      var opt_val = msg.option_value;
      if (this.slick_grid.getOptions()[opt_name] != opt_val) {
        this.slick_grid.setOptions({[opt_name]: opt_val});
        this.slick_grid.resizeCanvas();
      }
    } else if (msg.type == 'change_selection') {
      this.ignore_selection_changed = true;
      this.slick_grid.setSelectedRows(msg.rows);
      if (msg.rows && msg.rows.length > 0) {
        this.slick_grid.scrollRowIntoView(msg.rows[0]);
      }
      this.ignore_selection_changed = false;
    } else if (msg.type == 'change_show_toolbar') {
      this.initialize_toolbar();
    } else if (msg.col_info) {
      var filter = this.filters[msg.col_info.name];
      filter.handle_msg(msg);
    }
  }

  reset_in_progress_button() {
    if (this.in_progress_btn){
      this.in_progress_btn.removeClass('disabled');
      this.in_progress_btn.text(
        this.in_progress_btn.attr('data-btn-text')
      );
      this.in_progress_btn = null;
    }
  }

  /**
   * Update the size of the dataframe.
   */
  update_size() {
    var row_height = this.grid_options.rowHeight;
    var min_visible = 'minVisibleRows' in this.grid_options ?
        this.grid_options.minVisibleRows : 8;
    var max_visible = 'maxVisibleRows' in this.grid_options ?
        this.grid_options.maxVisibleRows : 15;

    var min_height = row_height * min_visible;
    // add 2 to maxVisibleRows to account for the header row and padding
    var max_height = 'height' in this.grid_options ? this.grid_options.height :
      row_height * (max_visible + 2);
    var grid_height = max_height;
    var total_row_height = (this.data_view.getLength() + 1) * row_height + 1;
    if (total_row_height <= max_height){
      grid_height = Math.max(min_height, total_row_height);
      this.grid_elem.addClass('hide-scrollbar');
    } else {
      this.grid_elem.removeClass('hide-scrollbar');
    }
    this.grid_elem.height(grid_height);
    this.slick_grid.render();
    this.slick_grid.resizeCanvas();
  }
}

// module.exports = {
//   XellgridModel : XellgridModel,
//   XellgridView : XellgridView
// };
