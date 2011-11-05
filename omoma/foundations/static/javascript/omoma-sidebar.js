function preparesideaccounts() {
    var directive = {'tr.siderow': {'account<-accounts': {'td.name':'account.name', 'td.value':'account.strbalance', 'td.value@title':'account.strbalancedefault'}}, 'tr.siderowtotal td.value':'total'}
    accountstemplate = $('div#sideaccounts table').compile(directive);
}
function preparesidecurrencies() {
    var directive = {'tr.siderow': {'currency<-context': {'td.name':'currency.name', 'td.value':'currency.rate'}}}
    currenciestemplate = $('div#sidecurrencies table').compile(directive);
}

function updatesideaccounts() {
    $.get('/json/accounts', function(data) {
        $('div#sideaccounts table').html(accountstemplate(data));
    });
}
function updatesidecurrencies() {
    $.get('/json/currencies', function(data) {
        $('div#sidecurrencies table').html(currenciestemplate(data));
    });
}

function updatesideall() {
    updatesideaccounts();
    updatesidecurrencies();
    // TODO Other boxes
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
    preparesidecurrencies();
    updatesidecurrencies();

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

    // Display accounts configuration dialog
    $('#currenciesopener').click(function(event) {
        opendialog("currencies", gettext("Configure my currencies"));
        $('div#dialogbox').bind('dialogclose', updatesidecurrencies);
        event.preventDefault();
    });

    // XXX Just for the demo, blinking for the community's header
    // Afterwards, blinking only when pending debts
    $('#sidecommunity h1').addClass('blink');

});
