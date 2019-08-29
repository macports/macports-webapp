var categorySearchTimer;

$(function () {
    $('#filter').keypress(function () {
        clearTimeout(categorySearchTimer);
        categorySearchTimer = setTimeout(function () {
            var data = {
                'name': $('#filter').val(),
                'categories__name': $('#categories__name').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            };
            var url = "/ports/filter/category/";
            ajaxCallSearchWithin(url, data);
        }, 1000);
    });
});
