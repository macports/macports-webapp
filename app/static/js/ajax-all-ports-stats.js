function runPortsSortAjax(page, order_by_1, order_by_2, order_by_3, days, search_by) {
    var currentSortAjaxRequest = null;
    currentSortAjaxRequest = $.ajax({
            type: 'GET',
            url: '/statistics/ports/filter',
            data: {
                'page': page,
                'order_by_1': order_by_1,
                'order_by_2': order_by_2,
                'order_by_3': order_by_3,
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
    var order_by_1 = $('.order_by_1').attr('id');
    var order_by_2 = $('.order_by_2').attr('id');
    var order_by_3 = $('.order_by_3').attr('id');
    var days = $('#days-filter').val();
    var search_by = $('#search-by').val();
    return {
        order_by_1: order_by_1,
        order_by_2: order_by_2,
        order_by_3: order_by_3,
        days: days,
        search_by: search_by
    }
}

$(function () {
    $('#table-header').ready(function () {
        var state = getPageState();
        runPortsSortAjax(1, state.order_by_1, state.order_by_2, state.order_by_3, state.days, state.search_by);
    });
});


function sort(e) {
    var new_order_1 = $(e).attr('id');
    var old_order_1 = $('.order_by_1').attr('id');
    var old_order_2 = $('.order_by_2').attr('id');
    var old_order_3 = $('.order_by_3').attr('id');
    if (new_order_1.replace('-', '') === old_order_1.replace('-', '')) {
        var order_by_2 = old_order_2;
        var order_by_3 = old_order_3;
        $('.order_by_1').removeClass('order_by_1');
        $(e).addClass('order_by_1');
    } else if (new_order_1.replace('-', '') === old_order_2.replace('-', '')) {
        var order_by_2 = old_order_1;
        var order_by_3 = old_order_3;
        $('.order_by_2').removeClass('order_by_2');
        $('.order_by_1').toggleClass('order_by_1 order_by_2');
        $(e).addClass('order_by_1');
    } else if (new_order_1.replace('-', '') === old_order_3.replace('-', '')) {
        var order_by_2 = old_order_1;
        var order_by_3 = old_order_2;
        $('.order_by_3').removeClass('order_by_3');
        $('.order_by_2').toggleClass('order_by_2 order_by_3');
        $('.order_by_1').toggleClass('order_by_1 order_by_2');
        $(e).addClass('order_by_1')
    }
    var days = $('#days-filter').val();
    var search_by = $('#search-by').val();
    runPortsSortAjax(1, new_order_1, order_by_2, order_by_3, days, search_by);
}

function changePage(page) {
    var state = getPageState();
    runPortsSortAjax(page, state.order_by_1, state.order_by_2, state.order_by_3, state.days, state.search_by);
}

$(function () {
    $('#days-filter').on('change', function () {
       var state = getPageState();
       runPortsSortAjax(1, state.order_by_1, state.order_by_2, state.order_by_3, state.days, state.search_by);
    });
});

$(function () {
    $('#search-by').keyup(function () {
        var state = getPageState();
        runPortsSortAjax(1, state.order_by_1, state.order_by_2, state.order_by_3, state.days, state.search_by);
    });
});
