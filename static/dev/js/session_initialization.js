$(document).ready(function () {
    $('.method').click(function () {
        var method = this.value;
        $.ajax({
            url: "/session-initialization/",
            data: {method: method},
            method: "GET",
            success: function (data) {
                console.log(data);
                if (data.error_message) {
                    //do some stuff
                    alert(data.error_message)
                } else {
                    document.getElementById("communication_method_" + data.approved_method).style.color = "blue"
                }
            }
        })

    });
    $('.session_initialization_button').click(function () {
        var form = $(this).closest("form");
        $.ajax({
            url: "/session-initialization/",
            data: form.serialize(),
            method: "POST",
            success: function (meta) {
                alert(meta.Session)
            }
        })
    });

});