import $ = require('jquery');
import filter_base = require('./xellgrid.filterbase');
import 'jqueryui';

export class DateFilter extends filter_base.FilterBase {
	public field: any;
	public min_value: any;
	public max_value: any;
	public filter_start_date: any;
	public filter_end_date: any;
	public has_multiple_values: any;
	public show_filter: any;
	public update_filter_button_disabled: any;
	public start_date_control: any;
	public min_date: any;
	public end_date_control: any;
	public max_date: any;
	public send_filter_changed: any;
	public filter_elem: any;

  get_filter_html() {
    return `
      <div class='date-range-filter grid-filter xellgrid-dropdown-menu'>
        <h3 class='xellgrid-popover-title'>
          <div class='dropdown-title'>Filter by ${this.field}</div>
          <i class='fa fa-times icon-remove close-button'/>
        </h3>
        <div class='dropdown-body'>
          <input class='datepicker ignore start-date'/>
          <span class='to'>to</span>
          <input class='datepicker ignore end-date'/>
        </div>
        <div class='dropdown-footer'>
          <a class='reset-link' href='#'>Reset</a>
        </div>
      </div>
    `;
  }

  update_min_max(col_info:any, has_active_filter:any) {
    this.min_value = col_info.filter_min;
    this.max_value = col_info.filter_max;

    var filter_info = col_info.filter_info;
    if (filter_info) {
      this.filter_start_date = filter_info.min || this.min_value;
      this.filter_end_date = filter_info.max || this.max_value;
    } else {
      this.filter_start_date = this.min_value;
      this.filter_end_date = this.max_value;
    }

    this.has_multiple_values = this.min_value != this.max_value;
    this.show_filter();
    if (has_active_filter) {
      this.update_filter_button_disabled();
    }
  }

  reset_filter() {
    this.start_date_control.datepicker("setDate", this.min_date);
    this.end_date_control.datepicker("setDate", this.max_date);

    this.start_date_control.datepicker("option", "maxDate", this.max_date);
    this.end_date_control.datepicker("option", "minDate", this.min_date);

    this.filter_start_date = null;
    this.filter_end_date = null;
    this.send_filter_changed();
  }

  initialize_controls() {
    super.initialize_controls();
    this.min_date = new Date(this.min_value);
    this.max_date = new Date(this.max_value);

    this.start_date_control = this.filter_elem.find(".start-date");
    this.end_date_control = this.filter_elem.find(".end-date");

    var date_options = {
      "dayNamesMin": ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      "prevText": "",
      "nextText": "",
      minDate: this.min_date,
      maxDate: this.max_date,
      beforeShow: (input:any, inst:any) => {
        // align the datepicker with the right edge of the input it drops down from
        var clicked_elem = $(inst);
        clicked_elem.closest(".xellgrid-dropdown-menu").addClass("calendar-open");

        var widget = clicked_elem.datepicker('widget');
        widget.css('margin-left', $(input).outerWidth()! - widget.outerWidth()!);
        widget.addClass("stay-open-on-click filter-child-elem");
      },
      onSelect: (dateText:any, instance:any) => {
        // pull the values from the datepickers
        var start_date_string = this.start_date_control.val();
        var end_date_string = this.end_date_control.val();

        var start_date = new Date(start_date_string);
        var end_date = new Date(end_date_string);

        var start_date_number = Date.UTC(start_date.getUTCFullYear(), start_date.getUTCMonth(), start_date.getUTCDate());
        var end_date_number = Date.UTC(end_date.getUTCFullYear(), end_date.getUTCMonth(), end_date.getUTCDate());
        end_date_number += (1000 * 60 * 60 * 24) - 1;

        this.filter_start_date = start_date_number;
        this.filter_end_date = end_date_number;

        this.send_filter_changed();

        var datepicker = $(instance.input);
        setTimeout((function () {
          datepicker.blur();
        }), 100);

        if (datepicker.hasClass("start-date")) {
          // update the end date's min
          this.end_date_control.datepicker("option", "minDate", start_date);
        }
        if (datepicker.hasClass("end-date")) {
          // update the start date's max
          this.start_date_control.datepicker("option", "maxDate", new Date(end_date_string));
        }
      }
    };

    this.filter_elem.find(".datepicker").datepicker(date_options);

    if (this.filter_start_date != null){
      this.start_date_control.datepicker("setDate", this.get_utc_date(this.filter_start_date));
    } else {
      this.start_date_control.datepicker("setDate", this.min_date);
    }

    if (this.filter_end_date != null){
      this.end_date_control.datepicker("setDate", this.get_utc_date(this.filter_end_date));
    } else {
      this.end_date_control.datepicker("setDate", this.max_date);
    }
  }

  get_utc_date(date_ms: any) {
    var date = new Date(date_ms);
    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
  }

  get_filter_info() {
    return {
      "field": this.field,
      "type": "date",
      "min": this.filter_start_date,
      "max": this.filter_end_date
    };
  }

  is_active() {
    return this.filter_start_date || this.filter_end_date;
  }
}

