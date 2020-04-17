var categorySearchTimer;

$(function () {
    $('#filter').keydown(function () {
        clearTimeout(categorySearchTimer);
        categorySearchTimer = setTimeout(function () {
            var data = {
                'name': $('#filter').val(),
                'categories__name': $('#categories__name').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            };
            var url = "/categories/search/";
            ajaxCallSearchWithin(url, data);
        }, 1000);
    });
});
