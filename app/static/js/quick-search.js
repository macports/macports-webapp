$(document).ready(function () {
    var queryPorts = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 20,
        rateLimitWait: 800,
        remote: {
            url: '/api/v1/autocomplete/port?q=%QUERY&name=on',
            wildcard: '%QUERY',
            filter: function (response) {
                return response.results;
            }
        }
    });

    queryPorts.initialize();

    $('#bloodhound .typeahead').typeahead({
            hint: true,
            highlight: true,
            minLength: 2,
        },
        {
            name: 'results',
            limit: 10,
            display: 'name',
            source: queryPorts.ttAdapter(),
            templates: {
                empty: [
                ].join('\n'),
                suggestion: Handlebars.compile(
                    '<div class="border-bottom search-result-item text-left">' +
                    '<div class="card-body py-1 px-2">' +
                    '<h6 class="mb-0 pb-0"><i class="fa fa-search mr-2 my-0"></i>{{name}} <a class="ml-2 btn btn-link text-secondary p-0 m-0" href="/port/{{name}}"><i class="fa fa-sign-in-alt"></i></a></h6>' +
                    '<span style="font-size: 13px" class="text-secondary">{{description}}</span>' +
                    '</div>' +
                    '</div>'
                )
            }
        }).on('typeahead:asyncrequest', function () {
            $('#search-spinner').show();
        }).on('typeahead:asynccancel typeahead:asyncreceive', function () {
            $('#search-spinner').hide();
        }).on('typeahead:select', function (evt, itm) {
            window.location.href = "/search/?q=" + itm.name + "&name=on";
        }).on('keyup', '.home-input-search', function (event) {
            if (event.key == "Enter") {
                $('#search_submit').click();
            }
        });
});
