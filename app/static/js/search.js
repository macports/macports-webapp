$(function () {
    let searchParams = new URLSearchParams(window.location.search);
    if(searchParams.has("selected_facets")) {
        let values = searchParams.getAll("selected_facets");
        for(index = 0; index<values.length; index++) {
            let v = values[index];
            let sections = v.split(':');
            let facet_query = sections[0];
            let facet_value = sections[1];
            switch(facet_query) {
                case "maintainers_exact":
                    if (sections.length < 2 || searchParams.get("nomaintainer") === "on") {
                        $('#m-facets').html("");
                    } else {
                        appendMaintainerFilter(facet_value);
                    }
                    break;
                case "categories_exact":
                    if (sections.length < 2) {
                        $('#c-facets').html("");
                    } else {
                        appendCategoryFilter(facet_value);
                    }
                    break;
                case "variants_exact":
                    if (sections.length < 2) {
                        $('#v-facets').html("");
                    } else {
                        appendVariantFilter(facet_value);
                    }
                    break;
            }
        }
    }

    $('#remove-maintainers-filter').on('click', function () {
        $('#m-facets').html("");
        $('#super-submit').click();
    });
    $('#remove-categories-filter').on('click', function () {
        $('#c-facets').html("");
        $('#super-submit').click();
    });
    $('#remove-variants-filter').on('click', function () {
        $('#v-facets').html("");
        $('#super-submit').click();
    });
});


$(document).ready(function () {
    var queryMaintainers = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('github'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 20,
        rateLimitWait: 800,
        remote: {
            url: '/api/v1/autocomplete/maintainer/?q=%QUERY',
            wildcard: '%QUERY',
            filter: function (response) {
                return response.results;
            }
        }
    });

    var queryCategories = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 20,
        rateLimitWait: 800,
        remote: {
            url: '/api/v1/autocomplete/category/?q=%QUERY',
            wildcard: '%QUERY',
            filter: function (response) {
                return response.results;
            }
        }
    });

    var queryVariants = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('variant'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 20,
        rateLimitWait: 800,
        remote: {
            url: '/api/v1/autocomplete/variant/?q=%QUERY',
            wildcard: '%QUERY',
            filter: function (response) {
                return response.results;
            }
        }
    });

    queryMaintainers.initialize();
    queryCategories.initialize();
    queryVariants.initialize();

    $('#maintainer-q').typeahead({
            hint: true,
            highlight: true,
            minLength: 2,
        },
        {
            name: 'results',
            limit: 10,
            display: 'github',
            source: queryMaintainers.ttAdapter(),
            templates: {
                empty: [].join('\n'),
                suggestion: Handlebars.compile(
                    '<div class="border-bottom text-left">' +
                    '<div class="card-body py-1 px-2">' +
                    '{{ github }}' +
                    '</div>' +
                    '</div>'
                )
            }
        }).on('typeahead:asyncrequest', function () {
        $('#maintainer-autocomplete-spinner').show();
    }).on('typeahead:asynccancel typeahead:asyncreceive', function () {
        $('#maintainer-autocomplete-spinner').hide();
    }).on('typeahead:select', function (evt, itm) {
        appendMaintainerFilter(itm.github);
        $('#super-submit').click();
    }).on('keydown', function (event) {
        if (event.keyCode == 13) {
            appendMaintainerFilter($('#maintainer-q').val());
            $('#super-submit').click();
        }
    });

    $('#category-q').typeahead({
            hint: true,
            highlight: true,
            minLength: 2,
        },
        {
            name: 'results',
            limit: 10,
            display: 'name',
            source: queryCategories.ttAdapter(),
            templates: {
                empty: [].join('\n'),
                suggestion: Handlebars.compile(
                    '<div class="border-bottom text-left">' +
                    '<div class="card-body py-1 px-2">' +
                    '{{ name }}' +
                    '</div>' +
                    '</div>'
                )
            }
        }).on('typeahead:asyncrequest', function () {
        $('#category-autocomplete-spinner').show();
    }).on('typeahead:asynccancel typeahead:asyncreceive', function () {
        $('#category-autocomplete-spinner').hide();
    }).on('typeahead:select', function (evt, itm) {
        appendCategoryFilter(itm.name);
        $('#super-submit').click();
    }).on('keydown', function (event) {
        if (event.keyCode == 13) {
            appendCategoryFilter($('#category-q').val());
            $('#super-submit').click();
        }
    });

    $('#variant-q').typeahead({
            hint: true,
            highlight: true,
            minLength: 2,
        },
        {
            name: 'results',
            limit: 10,
            display: 'variant',
            source: queryVariants.ttAdapter(),
            templates: {
                empty: [].join('\n'),
                suggestion: Handlebars.compile(
                    '<div class="border-bottom text-left">' +
                    '<div class="card-body py-1 px-2">' +
                    '{{ variant }}' +
                    '</div>' +
                    '</div>'
                )
            }
        }).on('typeahead:asyncrequest', function () {
        $('#variant-autocomplete-spinner').show();
    }).on('typeahead:asynccancel typeahead:asyncreceive', function () {
        $('#variant-autocomplete-spinner').hide();
    }).on('typeahead:select', function (evt, itm) {
        appendVariantFilter(itm.variant);
        $('#super-submit').click();
    }).on('keydown', function (event) {
        if (event.keyCode == 13) {
            appendVariantFilter($('#variant-q').val());
            $('#super-submit').click();
        }
    });
});


function appendMaintainerFilter(facet_value) {
    if (facet_value === "") {
        $('#m-facets').html("");
    } else {
        $('#m-facets').html([
                'Selected maintainer: <strong>',
                facet_value,
                '</strong> <input form="super-form" style="display: none" class="disabled" name="selected_facets" value=',
                'maintainers_exact:' + facet_value,
                '>',
                '<button id="remove-maintainers-filter"',
                'class="btn btn-lg p-0 text-danger btn-link"><i class="fa fa-window-close"></i></button>'
            ].join(' ')
        );
    }
}


function appendCategoryFilter(facet_value) {
    if (facet_value === "") {
        $('#c-facets').html("");
    } else {
        $('#c-facets').html([
                'Selected category: <strong>',
                facet_value,
                '</strong> <input form="super-form" style="display: none" class="disabled" name="selected_facets" value=',
                'categories_exact:' + facet_value,
                '>',
                '<button id="remove-categories-filter"',
                'class="btn btn-lg p-0 text-danger btn-link"><i class="fa fa-window-close"></i></button>'
            ].join(' ')
        );
    }

}

function appendVariantFilter(facet_value) {
    if (facet_value === "") {
        $('#v-facets').html("");
    } else {
        $('#v-facets').html([
                'Selected variant <strong>',
                facet_value,
                '</strong> <input form="super-form" style="display: none" class="disabled" name="selected_facets" value=',
                'variants_exact:' + facet_value,
                '>',
                '<button id="remove-variants-filter"',
                'class="btn btn-lg p-0 text-danger btn-link"><i class="fa fa-window-close"></i></button>'
            ].join(' ')
        );
    }
}
