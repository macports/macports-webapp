var requestTimer;

function ajaxCallSearch() {
    var data = {};
    var currentSearchRequest = null;
    var search = $('#search').val();
    data[$("input[name=search_by]:checked").val()] = search;
    data['csrfmiddlewaretoken'] = $("input[name=csrfmiddlewaretoken]").val();
    data['search_by'] = $("input[name=search_by]:checked").val();
    data['search_text'] = search;
    
    updateLocation();

    if (search) {
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
    var params = new URLSearchParams(location.search.substring(1));
    var search = params.get('search');
    var defaultSearchBy = $("input[name=search_by]:checked").val();
    var otherSearchBy = $("input[name=search_by]:not(:checked)").val();
    var searchBy = params.get('search_by') === otherSearchBy ? otherSearchBy : defaultSearchBy;
    
    $('#search')
        .keydown(function () {
            clearTimeout(requestTimer);
            requestTimer = setTimeout(function () {
                ajaxCallSearch();
            }, 1000);
        })
        .val(search);    
    $("input[name=search_by][value=" + searchBy + "]").prop("checked", true);
    
    updateLocation(true);
    
    if (search) {
        ajaxCallSearch();
    }
});

function searchSuccess(data, textStatus, jqXHR) {
    $('#filtered_table').html(data);
    $('#searching-image').hide();
}

function cancel_search() {
    $('#filtered_table').hide();
    $('#main-content').show();
    $('#search').val('');
    updateLocation();
}

function switch_search() {
    ajaxCallSearch();
}

function updateLocation(replace) {
    var url = new URL(location);
    var search = $('#search').val();
    if (search) {
        url.searchParams.set('search', search);
        url.searchParams.set('search_by', $("input[name=search_by]:checked").val());
    } else {
        url.searchParams.delete('search');
        url.searchParams.delete('search_by');
    }
    
    if (replace) {
        history.replaceState(null, '', url.href);
    } else {
        history.pushState(null, '', url.href);
    }
}

