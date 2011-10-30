function preparesideaccounts() {
    var directive = {'tr.siderow': {'account<-accounts': {'td.name':'account.name', 'td.value':'account.strbalance'}}, 'tr.siderowtotal td.value':'total'}
    accountstemplate = $('div#sideaccounts table').compile(directive);
}
function updatesideaccounts() {
    $.get('/json/accounts', function(data) {
        $('div#sideaccounts table').html(accountstemplate(data));
    });
}

$(document).ready(function() {
    // Sortable sidebar elements
    $('div#sidebar').sortable({handle: 'h1', containment:'parent', distance: 10, placeholder:'sideplaceholder', opacity: 0.5, update: function () { order = $('div#sidebar').sortable('toArray'); $.get('/sidebar/updateorder/'+order.toString()); } });

    // Initialize sidebar elements content
    $('div#sideaccounts > h1 > span.sideboxtitle').html('Accounts');
    $('div#sideenvelopes > h1 > span.sideboxtitle').html('Envelopes');
    $('div#sidecategories > h1 > span.sideboxtitle').html('Categories');
    $('div#sidecommunity > h1 > span.sideboxtitle').html('Community');
    $('div#sidecurrencies > h1 > span.sideboxtitle').html('Currencies');

    // Icons for sidebox
    $('span.sideboxopencloseicon > span').addClass('ui-icon-triangle-1-n');
    $('div.sidecontent.hidden span.sideboxopencloseicon > span').removeClass('ui-icon-triangle-1-n').addClass('ui-icon-triangle-1-s');

    // Update sideboxes content
    preparesideaccounts();
    updatesideaccounts();
    // TODO Other boxes

    // Toggle sidebox visibility
    $('div.sidecontent span.sideboxopencloseicon > span').click( function (event) {
        var icon = $(this);
        icon.parents('div.sidecontent').toggleClass('hidden');
        icon.toggleClass('ui-icon-triangle-1-n');
        icon.toggleClass('ui-icon-triangle-1-s');
        $.get('/sidebar/toggle/'+icon.parents('div.sidecontent').attr('id'));
    });

    // Display accounts configuration dialog
    $('#accountsopener').click(function(event) {
        opendialog("accounts", gettext("Configure accounts"));
        $('div#dialogbox').bind('dialogclose', updatesideaccounts);
        event.preventDefault();
    });

});
