function ajaxCall() {
    var data = {};
    data[$("input[name=search_by]:checked").val()] = $('#search').val();
    data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
    data['search_by'] = $("input[name=search_by]:checked").val();
    data['search_text'] = $('#search').val()

    if ($('#search').val()) {
            $('#filtered_table').show();
            $('#main-content').hide();
            $.ajax({
                type: 'POST',
                url: '/ports/search/',
                data: data,
                success: searchSuccess,
                beforeSend: function () {
                    $('#filtered_table').html("Searching ...")
                },
                dataType: 'html'
            });
        } else {
            $('#filtered_table').hide();
            $('#main-content').show();
        }
}

$(function () {
    $('#search').keyup(function () {
        ajaxCall()
    });
});

function searchSuccess(data, textStatus, jqXHR) {
    $('#filtered_table').html(data);
}

function cancel_search() {
    $('#filtered_table').hide();
    $('#main-content').show();
    $('#search').val('');
}

function switch_search() {
    ajaxCall()
}
