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

function tabClick(e, slug) {
    $('.active').removeClass("active");
    $(e).addClass("active");
    ajaxCall("/port/ajax-call/" + slug)
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

//Load Trac Tickets
function loadTickets(e) {
    $('.active').removeClass("active");
    $(e).addClass("active");
    $.ajax({
        type: 'POST',
        url: '/ports/load_tickets/',
        data: {
            'portname': $('#port_name').text(),
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: showTickets,
        beforeSend: function () {
            $('#display-box').html("");
            $('#loading-image').show();
        },
        dataType: 'html'
    });
};

function showTickets(data, textStatus, jqXHR) {
    $('#display-box').html(data);
    $('#loading-image').hide();
}