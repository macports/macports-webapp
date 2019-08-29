var variantSearchTimer;

$(function () {
    $('#filter').keypress(function () {
        clearTimeout(variantSearchTimer);
        variantSearchTimer = setTimeout(function () {
            var data = {
                'name': $('#filter').val(),
                'variant': $('#search_in').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            };
            var url = "/ports/filter/variant/";
            ajaxCallSearchWithin(url, data);
        }, 1000);
    });
});
