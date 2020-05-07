$(document).ready(function () {
    var queryPorts = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 20,
        rateLimitWait: 800,
        remote: {
            url: '/api/v1/search/?q=%QUERY&name=on&description=on&maintainers=on',
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
            minLength: 1,
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
                    '<a class="btn btn-link text-primary p-0" href="/port/{{name}}"><h5>{{name}}</h5></a>' +
                    '<p class="mb-0" style="font-size: 16px">{{description}}</p>' +
                    '<span style="font-size: 13px">' +
                    '<strong>Maintained by: </strong>' +
                    '{{#each maintainers}}' +
                    '<a href="/maintainers/github/{{this}}">{{ this }}, </a>' +
                    '{{/each}}' +
                    ` | ` +
                    '<strong>Variants: </strong>' +
                    '{{#each variants}}' +
                    '<a href="/variant/v/{{this}}">{{ this }}</a>' +
                    '{{/each}}' +
                    '</span>' +
                    '</div>' +
                    '</div>'
                )
            }
        }).on('typeahead:asyncrequest', function () {
        $('#search-spinner').show();
        }).on('typeahead:asynccancel typeahead:asyncreceive', function () {
        $('#search-spinner').hide();
        });
});
