$(document).ready(function () {
    $('.com_method_ajax').click(function () {
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
                }
                else {
                    document.getElementById("id_"+data.approved_method).style.color = "blue"
                }
            }
        })

    })

});