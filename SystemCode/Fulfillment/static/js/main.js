(function ($) {

    $(".ping").click(function () {

        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {

            displayText = "";
            if (xmlHttp.readyState < 4) {
                displayText = "RASA server is starting up";
                color = "yellow"
            } else if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
                displayText = "RASA server is running";
                color = "green"
            } else if (xmlHttp.readyState == 4 && xmlHttp.status >= 400){
                displayText = "RASA server is unable to start";
                color = "red"
            } else if (xmlHttp.readyState == 4 && xmlHttp.status == 0) {
                displayText = "RASA server CORS is not enabled";
                color = "red"
            }
            console.log("readyState: " + xmlHttp.readyState + ", status:" + xmlHttp.status)

            $("#status").text(displayText);
            $("#status").css("color", color);
        }
        xmlHttp.open("GET", "https://testshop1606.herokuapp.com", true); // true for asynchronous
        xmlHttp.send(null);
    });
})(jQuery);
