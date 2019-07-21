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
    history.pushState(null, null, "?tab=" + slug)
}

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
            $('#tickets-box').html("Please wait while tickets are fetched from Trac");
        },
        dataType: 'html'
    });
};

function receiveTickets(data, textStatus, jqXHR) {
    $('#tickets-box').html(data);
    var count = $('#tickets-count-returned').text();
    $('#tickets-count').html(count);
}

function showTickets(e) {
    $('.active').removeClass("active");
    $(e).addClass("active");
    $('#display-box').html("");
    $('#tickets-box').show();
    history.pushState(null, null, "?tab=tickets")
    
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

function installationStatsAjax() {
    var currentinstallationStatsAjax = null;

    currentinstallationStatsAjax = $.ajax({
        type: 'GET',
        url: '/port/ajax-call/stats/',
        data: {
            'port_name': $('#port_name').text(),
            'days': $('#days').val(),
            'days_ago': $('#days-ago').val(),
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: display,
        beforeSend: function () {
                $('#display-box').html("");
                $('#loading-image').show();
                if (currentinstallationStatsAjax != null) {
                    currentinstallationStatsAjax.abort();
                }
            },
        dataType: 'html'
    });
}
