// Open a dialog window
function opendialog(page, title) {
    $("div#dialogbox").load("/dialog/"+page+"/", function() {
        $("div#dialogbox").dialog({modal: true, resizable: false, position: "center", title: title});
    });
}

function dialogform(name, notice) {
    $('form#'+name+'form').ajaxForm(function(responseText) {
        $("div#dialogbox").html(responseText);
    });
    $("div#"+notice).delay(2000).fadeOut(500);
}

$(document).ready(function() {
    $("#details").tabs(); // Details tabs on the homepage
    // Header links
    $('#profileopener').click(function(event) { opendialog("profile", gettext("Profile and preferences")); event.preventDefault(); });
    $('#loginopener').click(function(event) { opendialog("login", gettext("Login")); event.preventDefault(); });
    $('#subscribeopener').click(function(event) { opendialog("subscribe", gettext("Subscribe")); event.preventDefault(); });
    //~ // Specific parts
    //~ updateinputelements();
});
