$(function () {
    $('#filter').keyup(function () {
        if ($('#filter').val()) {
            $('#filtered_table').show();
            $('#all_ports_table').hide();
            $.ajax({
                type: 'GET',
                url: '/ports/filter/category/',
                data: {
                    'name': $('#filter').val(),
                    'categories__name': $('#categories__name').text(),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccess,
                beforeSend: function() {
                    $('#filtered_table').html("Searching ...")
                },
                dataType: 'html'
        });
        } else {
            $('#filtered_table').hide();
            $('#all_ports_table').show();
        }
    });
});

function searchSuccess(data, textStatus, jqXHR) {
    $('#filtered_table').html(data);
}

function cancel_search() {
    $('#filtered_table').hide();
    $('#all_ports_table').show();
    $('#category_filter').val('');
}