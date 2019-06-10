$(function () {
    $('#search').ready(function () {
        $.ajax({
            type: 'POST',
            url: '/ports/load_tickets/',
            data: {
                'portname': $('#port_name').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: showTickets,
            beforeSend: function() {
                $('#trac_tickets').html("Loading Tickets From Trac ...")
            },
            dataType: 'html'
        });
    });
});

// Ajax request for the tabs
function ajaxCall(url) {
    var currentRequest = null;

    currentRequest = $.ajax({
            type: 'GET',
            url: url,
            data: {
                'portname': $('#port_name').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: display,
            beforeSend: function() {
                $('#display-box').html("");
                $('#loading-image').show();
                if(currentRequest != null) {
                    currentRequest.abort();
                }
            },
            dataType: 'html',
        });
}

function tabClick(e) {
    $('.active').removeClass("active");
    $(e).addClass("active");
    var slug = $(e).attr('id');
    ajaxCall("/port/ajax-call/" + slug)
}

function showTickets(data, textStatus, jqXHR) {
    $('#trac_tickets').html(data);
}

$(function () {
    $('#search').ready(function () {
        ajaxCall("/port/ajax-call/summary")
    });
});

function display(data, textStatus, jqXHR) {
    $('#display-box').html(data);
    $('#loading-image').hide();
}