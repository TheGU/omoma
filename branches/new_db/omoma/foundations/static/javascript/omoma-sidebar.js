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

    // Icons for sidebox
    $('span.sideboxopencloseicon').addClass('ui-icon-triangle-1-n');
    $('div.sidecontent.hidden span.sideboxopencloseicon').removeClass('ui-icon-triangle-1-n').addClass('ui-icon-triangle-1-s');

    // Update sideboxes content
    preparesideaccounts();
    updatesideaccounts();
    // TODO Other boxes


    // Toggle sidebox visibility
    $('div.sidecontent h1').click( function (event) {
        $(this).parents('div.sidecontent').toggleClass('hidden');
        icon = $(this).find('span.sideboxopencloseicon');
        icon.toggleClass('ui-icon-triangle-1-n');
        icon.toggleClass('ui-icon-triangle-1-s');
        $.get('/sidebar/toggle/'+$(this).parents('div.sidecontent').attr('id'));
    });
});









//~
//~
//~ function setaccountsopener() {
    //~ $('#accountsopener').click(function(event) {
        //~ $("div#dialogbox").load("{% url configureaccounts %}", function() {
            //~ $("div#dialogbox").dialog({modal: true, resizable: false, position: "center", width:500, title: gettext("Configure&nbsp;accounts"), close: function() {
                //~ if ($('img#sidemenuicon_accounts').hasClass('activesidemenu')) {
                    //~ $('div#accountssidecontainer').load('/sidebar/accounts/');
                //~ };
            //~ }});
        //~ });
//~
        //~ event.preventDefault();
    //~ });
//~ }
//~
//~
