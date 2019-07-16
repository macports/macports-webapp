function runPortsSortAjax(page, order_by, days, search_by) {
    var currentSortAjaxRequest = null;
    currentSortAjaxRequest = $.ajax({
            type: 'GET',
            url: '/statistics/ports/filter',
            data: {
                'page': page,
                'order_by': order_by,
                'days': days,
                'search_by': search_by,
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: portsSortAjaxSuccess,
            beforeSend: function () {
                $('#list-of-ports').html('');
                $('#loading-image').show();
                if(currentSortAjaxRequest != null) {
                    currentSortAjaxRequest.abort();
                }
            },
            dataType: 'html'
        });
}

function portsSortAjaxSuccess(data, textStatus, jqXHR) {
    $('#list-of-ports').html($(data).filter('#response-table').html());
    $('#navigation').html($(data).filter('#navigation-source').html());
    $('#loading-image').hide();
}

function getPageState() {
    var order_by = $('.btn-info').attr('id');
    var days = $('#days-filter').val();
    var search_by = $('#search-by').val();
    return {order_by:order_by, days:days, search_by:search_by}
}

$(function () {
    $('#table-header').ready(function () {
        var state = getPageState();
        runPortsSortAjax(1, state.order_by, state.days, state.search_by);
    });
});


function sort(e) {
    var order_by = $(e).attr('id');
    $('.btn-info').removeClass('btn-info');
    $(e).addClass('btn-info');
    var days = $('#days-filter').val();
    var search_by = $('#search-by').val();
    runPortsSortAjax(1, order_by, days, search_by);
}

function changePage(page) {
    var state = getPageState();
    runPortsSortAjax(page, state.order_by, state.days, state.search_by);
}

$(function () {
    $('#days-filter').on('change', function () {
       var state = getPageState();
       runPortsSortAjax(1, state.order_by, state.days, state.search_by);
    });
});

$(function () {
    $('#search-by').keyup(function () {
        var state = getPageState();
        runPortsSortAjax(1, state.order_by, state.days, state.search_by);
    });
});
