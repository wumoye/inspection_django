jQuery(document).ajaxSend(function (event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
$('#flip').on('click', function (e) {
    e.preventDefault();
    var card = $('#card');
    card.toggleClass('flipped');
    $('#login-img').toggleClass('flipped');
    if (card.hasClass("flipped")) {
        var fingerprintLable = $("#fingerprintLogin");
        var fingerprintdata = $("#fingerprintDataLogin");
        $.ajax({
            url: "/user/login",
            type: 'GET',
            data: $('#formLogin').serialize(),
            success: function (data) {
                // state.prop("hidden", true);
                var obj = JSON.parse(data);
                if (obj.status) {
                    // location.reload();
                    fingerprintLable.attr("value", obj.finger_code);
                    fingerprintdata.attr("value", obj.finger_code)
                } else {
                    $('#error_msg').text(obj.error);
                }
            }
        })
    }


});
$('#fingerRegister').click(function () {
    var chk = $("#fingerRegister");
    var checked = chk.is(':checked');
    var getFinger = $("#getFinger");
    var fingerDataShow = $("#fingerDataShow");
    if (checked) {
        fingerDataShow.prop("hidden", false);
        getFinger.prop("hidden", false);
    } else {
        fingerDataShow.prop("hidden", true);
        getFinger.prop("hidden", true);
    }
});
$.ajaxSetup({
    data: {csrfmiddlewaretoken: '{{ csrf_token }}'},
});

$('#getFinger').click(function () {
    var getFinger = $("#getFinger");
    var gettingFiner = $("#gettingFiner");
    var fingerData = $("#fingerData");
    var fingerDataShow = $("#fingerDataShow");
    gettingFiner.prop("hidden", true);
    $.ajax({
        url: "/user/register",
        type: 'GET',
        data: $('#formRegister').serialize(),
        success: function (data) {
            // state.prop("hidden", true);
            var obj = JSON.parse(data);
            if (obj.status) {
                // location.reload();
                fingerDataShow.html(obj.finger_code);
                fingerData.attr("value", obj.finger_code)
                getFinger.prop("hidden", true);
            } else {
                $('#error_msg').text(obj.error);
            }
        }
    })
});