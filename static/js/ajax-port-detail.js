// Ajax request for the tabs
function ajaxCall(url) {
    var currentRequest = null;

    currentRequest = $.ajax({
            type: 'GET',
            url: url,
            data: {
                'port_name': $('#port_name').text(),
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
    $('#tickets-box').hide();
}


$(function () {
    $('#search').ready(function () {
        ajaxCall("/port/ajax-call/summary")
        loadTickets();
        $('#tickets-box').hide()
    });
});

function display(data, textStatus, jqXHR) {
    $('#display-box').html(data);
    $('#loading-image').hide();
}

//Load Trac Tickets
function loadTickets() {
    $.ajax({
        type: 'GET',
        url: '/ports/load_tickets/',
        data: {
            'port_name': $('#port_name').text(),
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: receiveTickets,
        beforeSend: function () {
            $('#display-box').html("");
            $('#loading-image').show();
        },
        dataType: 'html'
    });
};

function receiveTickets(data, textStatus, jqXHR) {
    $('#tickets-box').html(data);
    var count = $('#tickets-count-returned').text();
    $('#tickets-count').html(count)
}

function showTickets(e) {
    $('.active').removeClass("active");
    $(e).addClass("active");
    $('#display-box').html("");
    $('#tickets-box').show();
    
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
            'port_name': $('#port_name').text(),
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