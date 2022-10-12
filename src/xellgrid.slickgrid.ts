import { random } from 'underscore';
import $ = require("jquery");
import date_filter = require('./xellgrid.datefilter');
import slider_filter = require('./xellgrid.sliderfilter');
import text_filter = require('./xellgrid.textfilter');
import boolean_filter = require('./xellgrid.booleanfilter');
import editors = require('./xellgrid.editors');
import moment = require('moment');
import { XellgridView } from './xellgrid.widget';


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


function create_data_view(df: any, df_range: any, df_length: any) {
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

function format_number(row: any, cell: any, value: any, columnDef: any, dataContext: any) {
    if (value === null){
      return 'NaN';
    }
    return value;
}

function format_string(row: any, cell: any, value: any, columnDef: any, dataContext: any) {
    return value;
}

function format_date(date_string: any, col_name: any, date_formats: any, slick_grid: any) {
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

    if (col_name in date_formats){
      var old_format = date_formats[col_name];
      if (date_format.length > old_format.length){
        date_formats[col_name] = date_format;
        setTimeout(() => {
          slick_grid.invalidateAllRows();
          slick_grid.render();
        }, 1);
      } else {
        date_format = date_formats[col_name];
      }
    } else {
      date_formats[col_name] = date_format;
    }

    return parsed_date.format(date_format);
}

function update_size(grid_options: any, data_view: any, grid_elem: any, slick_grid: any) {
    var row_height = grid_options.rowHeight;
    var min_visible = 'minVisibleRows' in grid_options ?
        grid_options.minVisibleRows : 8;
    var max_visible = 'maxVisibleRows' in grid_options ?
        grid_options.maxVisibleRows : 15;

    var min_height = row_height * min_visible;
    // add 2 to maxVisibleRows to account for the header row and padding
    var max_height = 'height' in grid_options ? grid_options.height :
      row_height * (max_visible + 2);
    var grid_height = max_height;
    var total_row_height = (data_view.getLength() + 1) * row_height + 1;
    if (total_row_height <= max_height){
      grid_height = Math.max(min_height, total_row_height);
      grid_elem.addClass('hide-scrollbar');
    } else {
      grid_elem.removeClass('hide-scrollbar');
    }
    grid_elem.height(grid_height);
    slick_grid.render();
    slick_grid.resizeCanvas();
}


function initialize_toolbar(model: any, tab: any, widget: any) {
    if (!model.show_toolbar){
      tab.removeClass('show-toolbar');
    } else {
      tab.addClass('show-toolbar');
    }

    let toolbar = $("<div class='xell-grid-toolbar'>").appendTo(tab);

    let window_dropdown_menu = $(`
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

    window_dropdown_menu.appendTo(toolbar);



   bind_toolbar_events(window_dropdown_menu, widget);
  }

function bind_toolbar_events(window_dropdown_menu: any, widget: any) {
    var that = widget
    let activated = false
    // this will find the element with class = main-menu
    window_dropdown_menu.main_menu_bar = window_dropdown_menu.find('ul.main-menu');
    window_dropdown_menu.main_menu_bar.mouseenter((e: any) =>{
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
        // that.main_menu.closeMainMenu();
      }
    });



    window_dropdown_menu.main_menu_bar.click((event: any) => {
      let target = $(event.target);
      if (!target.hasClass('active-menu') && !target.parents().hasClass('active-menu')) {
        widget.send({'type': event.target.getAttribute("value")})
      }
    });


  }




export function create_new_grid(model: any, xellGrid: XellgridView, json_df: any) {
    // $("div#xellgrid-tabs").tabs()
    var num = random(10000);
    // $("div#xellgrid-tabs ul#xell-grid-ul").append(
    //     "<li class='ui-tabs-tab ui-corner-top ui-state-default ui-tab'><a href='#tab" + num + "', class='ui-tabs-anchor'>Grid " + num + "</a></li>"
    // );
    
    // let tab_wrapper = $(`<div id="tab${num}" class="ui-tabs-panel ui-corner-bottom ui-widget-content">
    //     </div>`).appendTo("div#xellgrid-tabs")

    // let tab = $(`<div id="Grid${num}" class="ui-widget show-toolbar"></div>`).appendTo(tab_wrapper)
    // initialize_toolbar(model, tab, xellGrid);
    // let grid_elem = $("<div class='xell-grid'>").appendTo(tab);
    // xellGrid.tabs.tabs()
    var li = "<li class='ui-tabs-tab ui-corner-top ui-state-default ui-tab'><a href='#tab" + num + "', class='ui-tabs-anchor'>Grid " + num + "</a></li>"
    $(li).appendTo(xellGrid.ul)
    let tab_wrapper = $(`<div id="tab${num}" class="ui-tabs-panel ui-corner-bottom ui-widget-content">
        </div>`).appendTo(xellGrid.tabs)

    let tab = $(`<div id="Grid${num}" class="ui-widget show-toolbar"></div>`).appendTo(tab_wrapper)
    initialize_toolbar(model, tab, xellGrid);
    let grid_elem = $("<div class='xell-grid'>").appendTo(tab);




    var slick_grid: any = null;
    let df_json = JSON.parse(json_df);
    
    let columns = model._columns;
    let data_view = create_data_view(df_json.data, model._df_range, model._row_count);
    let grid_options = model.grid_options;
    let index_col_name = model._index_col_name;
    let row_styles = model._row_styles;

    let df_columns: any = [];
    let index_columns: any = [];
    let df_filter: any = {};
    let filter_list: any = [];
    let date_formats: any = {};
    let last_vp: any = null;
    let sort_in_progress: boolean = false;
    let sort_indicator = null;
    let resizing_column: boolean = false;
    let ignore_selection_changed: boolean = false;
    let vp_response_expected: boolean = false;
    // var next_viewport_msg = null;
    var viewport_timeout: any =  null;
    var number_type_info = {
      filter: slider_filter.SliderFilter,
      validator: editors.validateNumber,
      formatter: format_number
    };

    
    let type_infos: any = {
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
        formatter: format_string
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
              var formatted_val = format_date(
                  this.date_value, args.column.field, date_formats, slick_grid
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
          return format_date(value, columnDef.name, date_formats, slick_grid);
        }
      },
      any: {
        filter: text_filter.TextFilter,
        editor: editors.SelectEditor,
        formatter: format_string
      },
      interval: {
        formatter: format_string
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
      if (cur_column.name == index_col_name){
        continue;
      }

      var type_info = type_infos[cur_column.type] || {};

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
            xellGrid
        );
        df_filter[slick_column.id] = cur_filter;
        filter_list.push(cur_filter);
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

        if (grid_options.boldIndex) {
            slick_column.cssClass += ' idx-col';
        }

        index_columns.push(slick_column);
        continue;
      }

      if (cur_column.editable == false) {
        slick_column.editor = null;
      }

      df_columns.push(slick_column);
    }

    if (index_columns.length > 0) {
      df_columns = index_columns.concat(df_columns);
    }

    // var row_count = 0;

    // set window.slick_grid for easy troubleshooting in the js console
    
    slick_grid = new Slick.Grid(
      grid_elem,
      data_view,
      df_columns,
      grid_options
    );
    grid_elem.data('slickgrid', slick_grid);

    if (grid_options.forceFitColumns){
      grid_elem.addClass('force-fit-columns');
    }

    if (grid_options.highlightSelectedCell) {
      grid_elem.addClass('highlight-selected-cell');
    }

    // compare to false since we still want to show row
    // selection if this option is excluded entirely
    if (grid_options.highlightSelectedRow != false) {
      grid_elem.addClass('highlight-selected-row');
    }

    setTimeout(() => {
      slick_grid.init();
      update_size(grid_options, data_view, grid_elem, slick_grid);
    }, 1);

    slick_grid.setSelectionModel(new Slick.RowSelectionModel());
    slick_grid.setCellCssStyles("grouping", row_styles);
    slick_grid.render();
    
    update_size(grid_options, data_view, grid_elem, slick_grid);

    var render_header_cell = (e: any, args: any) => {
      var cur_filter = df_filter[args.column.id];
        if (cur_filter) {
          cur_filter.render_filter_button($(args.node), slick_grid);
        }
    };

    if (grid_options.filterable != false) {
      slick_grid.onHeaderCellRendered.subscribe(render_header_cell);
    }

    // Force the grid to re-render the column headers so the
    // onHeaderCellRendered event is triggered.
    slick_grid.setColumns(slick_grid.getColumns());

    $(window).resize(() => {
      slick_grid.resizeCanvas();
    });

    slick_grid.setSortColumns([]);

    let grid_header = xellGrid.$el.find(`#Grid${num}.slick-header-columns`);
    console.log("grid_header,", grid_header);
    
    var handle_header_click = (e: any) => {
      if (resizing_column) {
        return;
      }

      if (sort_in_progress){
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

      sort_in_progress = true;

      if (xellGrid.sorted_column == column){
        xellGrid.sort_ascending = !xellGrid.sort_ascending;
      } else {
        xellGrid.sorted_column = column;
        if ('defaultSortAsc' in column) {
            xellGrid.sort_ascending = column.defaultSortAsc;
        } else{
            xellGrid.sort_ascending = true;
        }
      }

      var all_classes = 'fa-sort-asc fa-sort-desc fa fa-spin fa-spinner';
      var clicked_column_sort_indicator = col_header.find('.slick-sort-indicator');
      if (clicked_column_sort_indicator.length == 0){
        clicked_column_sort_indicator =
            $("<span class='slick-sort-indicator'/>").appendTo(col_header);
      }

      sort_indicator = clicked_column_sort_indicator;
      sort_indicator.removeClass(all_classes);
      grid_elem.find('.slick-sort-indicator').removeClass(all_classes);
      sort_indicator.addClass(`fa fa-spinner fa-spin`);
      var msg = {
        'type': 'change_sort',
        'sort_field': xellGrid.sorted_column.field,
        'sort_ascending': xellGrid.sort_ascending,
        'title': model.title
      };
      xellGrid.send(msg);
    };

    if (grid_options.sortable != false) {
      grid_header.click(handle_header_click)
    }

    var contextMenuOptions = {
      // optionally and conditionally define when the the menu is usable,
      // this should be used with a custom formatter to show/hide/disable the menu
      commandTitle: "Commands",
      // which column to show the command list? when not defined it will be shown over all columns
      commandItems: [
        { command: "remove_row", title: "Delete A Row",
          action: (e: any, args: any) => {
            xellGrid.send({'type': "remove_row",
                           'title': model.title})
          }
        },
        { command: "add_empty_row", title: "Add An Empty Row", iconImage: "", cssClass: "bold", textCssClass: "red",
          action: (e: any, args: any) => {
            xellGrid.send({
              'type': "add_empty_row",
              'row': args.row,
              'title': model.title
            })
          }
        },
        { 
          command: "add_row", title: "Duplicate Last Row", iconImage: "", cssClass: "bold", textCssClass: "red",
          action: (e: any, args: any) => {
            xellGrid.send({'type': "add_row",
                           'title': model.title})
          }
        },
        {
          command: "add_new_tab", title: "Add New Tab", iconImage: "", cssClass: "", textCssClass: "",
          action: (e: any, args: any) => {
            // add_new_slick_grid(model, this.init_df);
            // this.send({'type': "add_new_tab"})
          }
        }, 
        {
          command: "delete_current_tab", title: "Delete Current Tab", iconImage: "", cssClass: "", textCssClass: "",
          action: (e: any, args: any) => {
            xellGrid.send({'type': "delete_current_tab",
                           'title': model.title})
          }
        },
        {
          command: "toggle_filter", title: "Filter", iconImage: "", cssClass: "", textCssClass: "",
          action: (e: any, args: any) => {
            $('.filter-button').each(function(){
              if ($(this).hasClass('hidden')){
                $(this).removeClass('hidden')
              } else {
                $(this).addClass('hidden')
              }
            })
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
    slick_grid.registerPlugin(contextMenuPlugin);
    contextMenuPlugin.onBeforeMenuShow.subscribe((e: any, args: any) =>{
      e.preventDefault();
      e.stopPropagation();
      // for example, you could select the row it was clicked with
      slick_grid.setSelectedRows([args.row], e.target); // select the entire row
      //slick_grid.setActiveCell(args.row, args.cell, false); // select the cell that the click originated
      console.log("Before the global Context Menu is shown", args);
    });
    contextMenuPlugin.onBeforeMenuClose.subscribe(function (e: any, args: any) {
      console.log("Global Context Menu is closing", args);
    });

    contextMenuPlugin.onAfterMenuShow.subscribe(function (e: any, args: any) {
      // for example, you could select the row it was clicked with
      // grid.setSelectedRows([args.row]); // select the entire row
      //slick_grid.setActiveCell(args.row, args.cell, false); // select the cell that the click originated
      console.log("After the Context Menu is shown", args);
    });


    slick_grid.onViewportChanged.subscribe((e: any) => {
      if (viewport_timeout){
        clearTimeout(viewport_timeout);
      }
      viewport_timeout = setTimeout(() => {
        last_vp = slick_grid.getViewport();
        console.log("last_vp", last_vp);
        
        var cur_range = model._viewport_range;

        if (last_vp.top != cur_range[0] || last_vp.bottom != cur_range[1]) {
          var msg = {
            'type': 'change_viewport',
            'top': last_vp.top,
            'bottom': last_vp.bottom,
            'title': model.title
          };
          if (vp_response_expected){
            // next_viewport_msg = msg
          } else {
            vp_response_expected = true;
            xellGrid.send(msg);
          }
        //   xellGrid.send(msg);
        }
        viewport_timeout = null;
      }, 100);
    });

    // set up callbacks
    let editable_rows = model._editable_rows;
    if (editable_rows && Object.keys(editable_rows).length > 0) {
      slick_grid.onBeforeEditCell.subscribe((e: any, args: any) => {
        editable_rows = model._editable_rows;
        return editable_rows[args.item[index_col_name]]
      });
    }

    slick_grid.onCellChange.subscribe((e: any, args: any) => {
      var column = df_columns[args.cell].name;
      var data_item = slick_grid.getDataItem(args.row);
      var msg = {'row_index': data_item.row_index, 'column': column,
                 'unfiltered_index': data_item[index_col_name],
                 'value': args.item[column], 'type': 'edit_cell',
                 'title': model.title};
      xellGrid.send(msg);
    });

    slick_grid.onSelectedRowsChanged.subscribe((e: any, args: any) => {
      if (!ignore_selection_changed) {
        var msg = {'rows': args.rows, 'type': 'change_selection',
                   'title': model.title};
        xellGrid.send(msg);
      }
    });

    setTimeout(() => {
        xellGrid.$el.closest('.output_wrapper')
          .find('.out_prompt_overlay,.output_collapsed').click(() => {
        setTimeout(() => {
          slick_grid.resizeCanvas();
        }, 1);
      });

      xellGrid.resize_handles = grid_header.find('.slick-resizable-handle');
      xellGrid.resize_handles.mousedown((e: any) => {
        resizing_column = true;
      });
      $(document).mouseup(() => {
        // wait for the column header click handler to run before
        // setting the resizing_column flag back to false
        setTimeout(() => {
          resizing_column = false;
        }, 1);
      });
    }, 1);

    // $("div#xellgrid-tabs").tabs("refresh");
    // xellGrid.tabs.tabs("refresh"))
    // xellGrid.tabs.resizeCanvas()
    return slick_grid
  }