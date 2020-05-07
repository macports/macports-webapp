$(document).ready(function () {
    var queryPorts = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 20,
        rateLimitWait: 800,
        remote: {
            url: '/api/v1/search/?q=%QUERY&name=on',
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
                    '<div class="alert alert-danger">',
                    '<h6>Sorry, could not find any results. You may want to try advanced search, or include more details.</h6>',
                    '</div>'
                ].join('\n'),
                suggestion: Handlebars.compile(
                    '<div class="card search-result-item text-left bg-light">' +
                    '<div class="card-body p-2">' +
                    '<a class="btn btn-link text-primary p-0 m-0" href="/port/{{name}}"><h5>{{name}}</h5></a>' +
                    '<p class="m-0 p-0">{{description}}</p>' +
                    '</div>' +
                    '</div>'
                )
            }
        }).on('typeahead:asyncrequest', function () {
            $('#search-spinner').show();
        }).on('typeahead:asynccancel typeahead:asyncreceive', function () {
            $('#search-spinner').hide();
        }).on('typeahead:select', function (evt, itm) {
            window.location.href = "/port/" + itm.name;
        });
});
