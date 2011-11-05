// Resize panels according to the window height
function setpanelssize() {
    mainmenu = $('div#mainmenu').height();
    submenu = $('div#submenu').height();
    panelcontainer = $('div#panelcontainer').height();
    transactionsheader = $('div#transactionsheader').height()
    $('div#panelcontainer').height($(window).height() - 45);
    $('div#maincontent').height(panelcontainer - 25 - mainmenu);
    $('div#maincontentwithsubmenu').height(panelcontainer - mainmenu - submenu - 40);
    $('div#transactions').height(panelcontainer - mainmenu - submenu - transactionsheader - 65);
}

$(document).ready(function() {
    // Main menu mouseover
    $('div#mainmenu img').mouseover(function() { menuname = this.id.substr(9); $('div#mainmenu span').hide(); $('span#menutext_'+menuname).show(); });
    // Set panels height according to window height
    setpanelssize();
    $(window).resize(function() { setpanelssize(); });
});
