$(function () {
    $('#category_filter').keyup(function () {
        if ($('#category_filter').val()) {
            $('#filtered_table').show();
            $('#all_ports_table').hide();
            $.ajax({
                type: 'POST',
                url: '/ports/filter/',
                data: {
                    'query': $('#category_filter').val(),
                    'search_in': $('#search_in').text(),
                    'content': $('#filter-content').text(),
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