var requestTimer;

function ajaxCallSearch() {
    var data = {};
    var currentSearchRequest = null;
    data[$("input[name=search_by]:checked").val()] = $('#search').val();
    data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
    data['search_by'] = $("input[name=search_by]:checked").val();
    data['search_text'] = $('#search').val()

    if ($('#search').val()) {
        $('#filtered_table').show();
        $('#main-content').hide();
        currentSearchRequest = $.ajax({
            type: 'GET',
            url: '/ports/search/',
            data: data,
            success: searchSuccess,
            beforeSend: function () {
                $('#filtered_table').html('');
                $('#searching-image').show();
                if (currentSearchRequest != null) {
                    currentSearchRequest.abort();
                }
            },
            dataType: 'html'
        });
    } else {
        $('#filtered_table').hide();
        $('#searching-image').hide();
        $('#main-content').show();
    }
}

$(function () {
    $('#search').keypress(function () {
        clearTimeout(requestTimer);
        requestTimer = setTimeout(function () {
            ajaxCallSearch();
        }, 1000);
    });
});

function searchSuccess(data, textStatus, jqXHR) {
    $('#filtered_table').html(data);
    $('#searching-image').hide();
}

function cancel_search() {
    $('#filtered_table').hide();
    $('#main-content').show();
    $('#search').val('');
}

function switch_search() {
    ajaxCallSearch()
}

