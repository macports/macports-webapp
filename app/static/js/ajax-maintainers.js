var maintainerSearchTimer;

$(function () {
    $('#filter').keydown(function () {
        clearTimeout(maintainerSearchTimer);
        maintainerSearchTimer = setTimeout(function () {
            var data = {
                'name': $('#filter').val(),
                'maintainers__name': $('#maintainers__name').text(),
                'maintainers__github': $('#maintainers__github').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            };
            var url = "/maintainers/search/";
            ajaxCallSearchWithin(url, data);
        }, 1000);
    });
});
