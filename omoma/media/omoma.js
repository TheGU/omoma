// Javascript for Omoma
// Copyright 2011 Sebastien Maccagnoni-Munch
//
// This file is part of Omoma.
//
// Omoma is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, version 3.
//
// Omoma is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Omoma. If not, see <http://www.gnu.org/licenses/>.

$(document).ready(function() {
    $('#notifications').children().click(function() {
        $(this).slideUp();
    });
});

$(document).ready(function() {
    $('body').ajaxSuccess(function() {
        // Update balances
        $.ajax({
            url: '/ajax/getbalances',
            dataType: 'json',
            global: false,
            success: function (data) {
                $('tr[id^="account"]').each(function () {
                    id = $(this).attr('id').substring(7);
                    $(this).children('.validatedbalance').empty();
                    $(this).children('.validatedbalance').append(data[id].validated);
                    $(this).children('.currentbalance').empty();
                    $(this).children('.currentbalance').append(data[id].current);
                });
            }
        });
        $.ajax({
            url: '/ajax/getnotifications',
            dataType: 'html',
            global: false,
            success: function (data) {
                //$('#notifications').slideUp();
                $('#notifications').replaceWith(data);
                //$('#notifications').slideDown();
                $('#notifications').children().click(function() {
                    $(this).slideUp();
                });
            }
        });
    });
});

function validate_transaction(tid) {
    $.getJSON('/ajax/validate/'+tid, function (data) {
        id = data[0].pk;
        if (data[0].fields.validated) {
            $('#'+id+' a.validatelink > img').attr('src', '/static/icon_validated.png');
            $('#'+id+' a.editlink').css('display', 'none');
            $('#'+id+' a.deletelink').css('display', 'none');
        } else {
            $('#'+id+' a.validatelink > img').attr('src', '/static/icon_notvalidated.png');
            $('#'+id+' a.editlink').css('display', 'inline');
            $('#'+id+' a.deletelink').css('display', 'inline');
        };
    });
};

function delete_transaction(tid) {
    $.get('/ajax/delete/'+tid, function() {
        $('tr#'+tid).find('td').wrapInner('<div style="display: block;" />')
                  .parent().find('td > div').slideUp(400, function() {
            $(this).parent().parent().remove();
        });
    });
};

function enable_transactionlinks() {
    $('.validatelink').unbind();
    $('.validatelink').click(function (event) {
        tid = $(this).parent().parent().attr('id');
        validate_transaction(tid);
        event.preventDefault();
    });
    $('.deletelink').unbind();
    $('.deletelink').click(function (event) {
        tid = $(this).parent().parent().attr('id');
        delete_transaction(tid);
        event.preventDefault();
    });
    $('.editlink').unbind();
    $('.editlink').click(function (event) {
        tid = $(this).parent().parent().attr('id');
        edit_transaction(tid);
        event.preventDefault();
    });
    $('.applylink').unbind();
    $('.applylink').click(function (event) {
        apply_edit_transaction(tid);
        event.preventDefault();
    });
    $('.cancellink').unbind();
    $('.cancellink').click(function (event) {
        tid = $(this).parent().parent().attr('id');
        cancel_edit_transaction(tid);
        event.preventDefault();
    });
    $('.iouicon').unbind();
    $('.iouicon').click(function (event) {
        tid = $(this).parent().parent().attr('id');
        toggle_ioudetails(tid);
    });
    $('.intable.date').datepicker($.datepicker.regional['fr']);
}


function toggle_ioudetails(tid) {
    $('tr#'+tid+' div.ioudetails').slideToggle('fast');
};

function edit_transaction(tid) {
    $.get('/ajax/edit/'+tid, function (data) {
        $(data).replaceAll('#'+tid);
        enable_transactionlinks();
    });
};

function apply_edit_transaction(tid) {
    // Could use "serialize()" here, but a form element inside a table row is impossible... :-(

    var csrfmiddlewaretoken = $('tr#'+tid+' input[name="csrfmiddlewaretoken"]').val();
    formdata = { csrfmiddlewaretoken: csrfmiddlewaretoken }

    var description = $('tr#'+tid+' input[name="description"]').val();
    if (description != '') { formdata.description = description }

    var peer1 = $('tr#'+tid+' select[name="peer1"]').val();
    if (peer1 != '') { formdata.peer1 = peer1 }

    var peer1amount = $('tr#'+tid+' input[name="peer1amount"]').val();
    if (peer1amount != '') { formdata.peer1amount = peer1amount }

    var peer2 = $('tr#'+tid+' select[name="peer2"]').val();
    if (peer2 != '') { formdata.peer2 = peer2 }

    var peer2amount = $('tr#'+tid+' input[name="peer2amount"]').val();
    if (peer2amount != '') { formdata.peer2amount = peer2amount }

    var peer3 = $('tr#'+tid+' select[name="peer3"]').val();
    if (peer3 != '') { formdata.peer3 = peer3 }

    var peer3amount = $('tr#'+tid+' input[name="peer3amount"]').val();
    if (peer3amount != '') { formdata.peer3amount = peer3amount }

    var peer4 = $('tr#'+tid+' select[name="peer4"]').val();
    if (peer4 != '') { formdata.peer4 = peer4 }

    var peer4amount = $('tr#'+tid+' input[name="peer4amount"]').val();
    if (peer4amount != '') { formdata.peer4amount = peer4amount }

    var peer5 = $('tr#'+tid+' select[name="peer5"]').val();
    if (peer5 != '') { formdata.peer5 = peer5 }

    var peer5amount = $('tr#'+tid+' input[name="peer5amount"]').val();
    if (peer5amount != '') { formdata.peer5amount = peer5amount }

    var transaction_type = $('tr#'+tid+' select[name="transaction_type"]').val();
    if (transaction_type != '') { formdata.transaction_type = transaction_type }

    var amount = $('tr#'+tid+' input[name="amount"]').val();
    if (amount != '') { formdata.amount = amount }

    var destination_account = $('tr#'+tid+' select[name="destination_account"]').val();
    if (destination_account != '') { formdata.destination_account = destination_account }

    var category1 = $('tr#'+tid+' select[name="category1"]').val();
    if (category1 != '') { formdata.category1 = category1 }

    var category1amount = $('tr#'+tid+' input[name="category1amount"]').val();
    if (category1amount != '') { formdata.category1amount = category1amount }

    var category2 = $('tr#'+tid+' select[name="category2"]').val();
    if (category2 != '') { formdata.category2 = category2 }

    var category2amount = $('tr#'+tid+' input[name="category2amount"]').val();
    if (category2amount != '') { formdata.category2amount = category2amount }

    var category3 = $('tr#'+tid+' select[name="category3"]').val();
    if (category3 != '') { formdata.category3 = category3 }

    var category3amount = $('tr#'+tid+' input[name="category3amount"]').val();
    if (category3amount != '') { formdata.category3amount = category3amount }

    var category4 = $('tr#'+tid+' select[name="category4"]').val();
    if (category4 != '') { formdata.category4 = category4 }

    var category4amount = $('tr#'+tid+' input[name="category4amount"]').val();
    if (category4amount != '') { formdata.category4amount = category4amount }

    var category5 = $('tr#'+tid+' select[name="category5"]').val();
    if (category5 != '') { formdata.category5 = category5 }

    var category5amount = $('tr#'+tid+' input[name="category5amount"]').val();
    if (category5amount != '') { formdata.category5amount = category5amount }

    var date = $('tr#'+tid+' input[name="date"]').val();
    if (date != '') { formdata.date = date }

    var account = $('tr#'+tid+' select[name="account"]').val();
    if (account != '') { formdata.account = account }
    
    $.post('/ajax/apply/'+tid+'/', formdata, function (data) {
        $(data).replaceAll('#'+tid);
        enable_transactionlinks();
    });
};

function cancel_edit_transaction(tid) {
    $.get('/ajax/cancel/'+tid, function (data) {
        $(data).replaceAll('#'+tid);
        enable_transactionlinks();
    });
};
