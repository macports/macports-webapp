function runPortsSortAjax(page, order_by, days=30) {
    var currentSortAjaxRequest = null;
    currentSortAjaxRequest = $.ajax({
            type: 'GET',
            url: '/statistics/ports/filter',
            data: {
                'page': page,
                'order_by': order_by,
                'days': days,
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

$(function () {
    $('#table-header').ready(function () {
        runPortsSortAjax(1, '-total_count', 30)
    });
});


function sort(e) {
    var order_by = $(e).attr('id');
    $('.btn-info').removeClass('btn-info');
    $(e).addClass('btn-info');
    var days = $('#days-filter').val();
    runPortsSortAjax(1, order_by, days);
}

function changePage(page) {
    var order_by = $('.btn-info').attr('id');
    var days = $('#days-filter').val();
    runPortsSortAjax(page, order_by, days);
}

$(function () {
    $('#days-filter').on('change', function () {
        var order_by = $('.btn-info').attr('id');
        var days = $('#days-filter').val();
        runPortsSortAjax(1, order_by, days);
    });
});
