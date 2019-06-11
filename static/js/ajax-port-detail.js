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

//Build History
function buildHistoryAjax(page) {
    var currentRequestBuild = null;

    currentRequestBuild= $.ajax({
        type: 'GET',
        url: '/port/ajax-call/builds/',
        data: {
            'builder_name__name': $('#builder-filter').val(),
            'status': $('#status-filter').val(),
            'portname': $('#port_name').text(),
            'page': page,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: display,
        beforeSend: function () {
                $('#display-box').html("");
                $('#loading-image').show();
                if(currentRequestBuild != null) {
                    currentRequestBuild.abort();
                }
            },
        dataType: 'html'
    });
}

function filterBuilds() {
    buildHistoryAjax(1);
}

function changePage(page) {
    buildHistoryAjax(page);
}