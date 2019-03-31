$(function () {
    $('#search').keyup(function () {
        if ($('#search').val()) {
            $('#search-results').show()
            $.ajax({
                type: 'POST',
                url: '/ports/search/',
                data: {
                    'search_text': $('#search').val(),
                     'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccess,
                beforeSend: function() {
                    $('#search-results').html("Searching ...")
                },
                dataType: 'html'
        });
        } else {
            $('#search-results').hide();
        }
    });
});

function searchSuccess(data, textStatus, jqXHR) {
    $('#search-results').html(data);
}