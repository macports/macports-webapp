function runAjax(page) {
    $.ajax({
            type: 'POST',
            url: '/ports/all_builds/filter/',
            data: {
                'builder_name__name': $('#builder-filter').val(),
                'status': $('#status-filter').val(),
                'port_name': $('#name-filter').val(),
                'page': page,
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: filterSuccess,
            beforeSend: function () {
                $('#all_builds_table').html("Loading...")
            },
            dataType: 'html'
        });
}

$(function () {
    $('.filter').on('change', function () {
        runAjax(1)
    });
});

$(function () {
    $('.filter').ready(function () {
        runAjax(1)
    });
});

$(function () {
    $('#name-filter').keyup(function () {
        runAjax(1)
    });
});

function changePage(page) {
    runAjax(page)
};

function filterSuccess(data, textStatus, jqXHR) {
    $('#all_builds_table').html(data);
}