$(function() {
    // Taken from pinax/js/theme.js
    $("#account_logout, .account_logout").click(function(e) {
        e.preventDefault();
        $("#accountLogOutForm").submit();
    });
});
