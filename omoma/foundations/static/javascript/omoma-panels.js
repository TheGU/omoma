// Resize panels according to the window height
function setpanelssize() {
    mainmenu = $('div#mainmenu').height(); submenu = $('div#submenu').height();
    $('div#panelcontainer').height($(window).height() - 45);
    $('div#maincontent').height($('div#panelcontainer').height() - 25 - mainmenu);
    $('div#maincontentwithsubmenu').height($('div#panelcontainer').height() - 40 - mainmenu - submenu);
}

$(document).ready(function() {
    // Main menu mouseover
    $('div#mainmenu img').mouseover(function() { menuname = this.id.substr(9); $('div#mainmenu span').hide(); $('span#menutext_'+menuname).show(); });
    // Set panels height according to window height
    setpanelssize();
    $(window).resize(function() { setpanelssize(); });
});
