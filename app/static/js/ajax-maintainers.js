$(function () {
    $('#filter').keyup(function () {
        if ($('#filter').val()) {
            $('#filtered_table').show();
            $('#all_ports_table').hide();
            $.ajax({
                type: 'GET',
                url: '/ports/filter/maintainer/',
                data: {
                    'name': $('#filter').val(),
                    'maintainers__name': $('#maintainers__name').text(),
                    'maintainers__github': $('#maintainers__github').text(),
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
    $('#filter').val('');
}
