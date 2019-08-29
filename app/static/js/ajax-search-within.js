function ajaxCallSearchWithin (url, data) {
    if ($('#filter').val()) {
        $('#filtered_table').show();
        $('#all_ports_table').hide();
        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: searchSuccess,
            beforeSend: function () {
                $('#searching-image').show();
                $('#filtered_table').html('');
                $('#all_ports_table').hide();
            },
            dataType: 'html'
        });
    } else {
        $('#filtered_table').hide();
        $('#all_ports_table').show();
    }
}

function searchSuccess(data, textStatus, jqXHR) {
    $('#searching-image').hide();
    $('#filtered_table').html(data);
}

function cancel_search() {
    $('#filtered_table').hide();
    $('#all_ports_table').show();
    $('#category_filter').val('');
}
