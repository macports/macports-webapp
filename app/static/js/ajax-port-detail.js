// Ajax used by Clicks on tabs : Summary and Builds
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
// End

function changePageState(e, state) {
    var port_name = $('#port_name').text();
    $('.active').removeClass("active");
    $(e).addClass("active");
    history.pushState(null, null, "/port/" + port_name + "/" + state);
}

function tabClick(e, slug) {
    changePageState(e, slug);
    $('#tickets-box').hide();
    ajaxCall("/port/ajax-call/" + slug + "/");
}

function display(data, textStatus, jqXHR) {
    $('#display-box').html(data);
    $('#loading-image').hide();
}

// Code for Tickets Start
function loadTickets() {
    $.ajax({
        type: 'GET',
        url: '/port/ajax-call/tickets',
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
    changePageState(e, "tickets")
    $('#display-box').html("");
    $('#tickets-box').show();
}
// Code for Tickets End

// Build History Filters Start
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
// Build History Filters End

// Installation Stats AJAX call and filters start
function installationStatsAjax(days=$('#days').val(), days_ago=$('#days-ago').val()) {
    var currentinstallationStatsAjax = null;

    currentinstallationStatsAjax = $.ajax({
        type: 'GET',
        url: '/port/ajax-call/stats/',
        data: {
            'port_name': $('#port_name').text(),
            'days': days,
            'days_ago': days_ago,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: display,
        beforeSend: function () {
                $('#display-box').html("");
                $('#loading-image').show();
                if (currentinstallationStatsAjax != null) {
                    currentinstallationStatsAjax.abort();
                }
                history.pushState(null, null, "?days=" + days + "&days_ago=" + days_ago)
            },
        dataType: 'html'
    });
}

function statsClick(e, days, days_ago) {
    changePageState(e, "stats");
    installationStatsAjax(days, days_ago);
    $('#tickets-box').hide();
}
// Installation Stats AJAX call and filters End

// Mouse over for closed maintainer
$(document).ready(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});
