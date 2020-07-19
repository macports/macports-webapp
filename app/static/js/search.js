$(function () {
    let searchParams = new URLSearchParams(window.location.search);
    if(searchParams.has("selected_facets")) {
        let values = searchParams.getAll("selected_facets");
        for(let index = 0; index<values.length; index++) {
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

    if(searchParams.has("installed_file")) {
        let ifValue = searchParams.get("installed_file");
        if (ifValue !== "") {
            $('#clear-installed-files-filter').show();
        }
    }

    if(searchParams.has("livecheck_outdated") || searchParams.has("livecheck_broken") || searchParams.has("livecheck_uptodate")) {
        let loValue = searchParams.get("livecheck_outdated");
        let lbValue = searchParams.get("livecheck_broken");
        let luValue = searchParams.get("livecheck_uptodate");
        if (loValue !== "" || lbValue !== "" || luValue !== "") {
            $('#clear-livecheck-filters').show();
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

    async function setFollowUnfollowButtons() {
        const response = await fetch( "/api/v1/user/followed_ports/");
        const data = await response.json();
        let ports = [];
        if ("ports" in data) ports =  data.ports;
        const ports_object = {};
        for (let i=0; i<ports.length; i++) {
            ports_object[ports[i]] = 1;
        }

        for (let i=1; i<=20; i++) {
            let box_id = "follow_port_" + i.toString();
            let e = document.getElementById(box_id);
            if (e === undefined) break;
            let port_name = e.getAttribute("data-name");
            if(!(port_name in ports_object)) {
                e.innerHTML = `<button onclick="ajaxFollowUnfollow('${port_name}', '${box_id}', 'follow');" class='btn text-light'><i class='fa fa-plus-circle'></i></button>`;
            } else {
                e.innerHTML = `<button onclick="ajaxFollowUnfollow('${port_name}', '${box_id}', 'unfollow');" class='btn text-secondary'><i class='fa fa-minus-circle'></i></button>`;
            }
        }

    }

    setFollowUnfollowButtons();
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

function clearLivecheck() {
    $("#id_livecheck_broken").prop("checked", false);
    $("#id_livecheck_outdated").prop("checked", false);
    $("#id_livecheck_uptodate").prop("checked", false);
    $("#super-submit").click();
}

function applyInstalledFilesFilter() {
    $("#super-submit").click();
}

function clearInstalledFilesFilter() {
    $("#id_installed_file").val("");
    $("#super-submit").click();
}

function ajaxFollowUnfollow(port_name, box_id, query) {
    let url = `/port/${port_name}/${query}/`;
    $.ajax({
        type: 'GET',
        url: url,
        indexValue: {
            port_name: port_name,
            box_id: box_id,
            query: query
        },
        data: {
            'basic': "on"
        },
        success: function () {
            let box_id = this.indexValue.box_id;
            let port_name = this.indexValue.port_name;
            let query = this.indexValue.query;
            let box = document.getElementById(box_id);
            setTimeout(function () {
                if (query === 'unfollow') {
                    box.innerHTML = `<button onclick="ajaxFollowUnfollow('${port_name}', '${box_id}', 'follow');" class='btn text-light'><i class='fa fa-plus-circle'></i></button>`;
                } else if (query === 'follow') {
                    box.innerHTML = `<button onclick="ajaxFollowUnfollow('${port_name}', '${box_id}', 'unfollow');" class='btn text-secondary'><i class='fa fa-minus-circle'></i></button>`;
                }
            }, 800);
        },
        beforeSend: function () {
            let box = document.getElementById(box_id);
            box.innerHTML = "";
            box.innerHTML = '<button class="btn"><img width="22" src="/static/images/tspinner.gif"></button>';
        },
        dataType: 'html'
    });
}
