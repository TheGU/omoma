function updateinputelements() {
    $.datepicker.setDefaults($.datepicker.regional[""]);
    $('input.date').datepicker({autoSize: true});
    $('input#filterdatestart').datepicker({autoSize: true,
                                                     changeMonth: true,
                                                     changeYear: true,
                                                     onSelect: function (selectedDate) {
        var date = $.datepicker.parseDate($.datepicker._defaults.dateFormat, selectedDate);
        $('input#filterdateend').datepicker( "option", 'minDate', date );
    }});
    $('input#filterdateend').datepicker({autoSize: true,
                                                     changeMonth: true,
                                                     changeYear: true,
                                                     onSelect: function (selectedDate) {
        var date = $.datepicker.parseDate($.datepicker._defaults.dateFormat, selectedDate);
        $('input#filterdatestart').datepicker( "option", "maxDate", date );

    }});

    // Amount input
    $('input.amount').setMask({mask: '99.999 999 999 999', type: 'reverse', defaultValue: '', autoTab: false, selectCharsOnFocus: true});
    // Category input
    $('input.category').autocomplete({source:"/json/categories", minLength: 0});
    $('input.category').focus(function() { $(this).autocomplete("search", ""); });
}

$(document).ready(function() { updateinputelements(); });
