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
                    if (facet_value === "" || sections.length < 2) {
                        $('#m-facets').html("");
                    } else {
                        $('#m-facets').html([
                                'Selected maintainer: <strong>',
                                facet_value,
                                '</strong> <input style="display: none" class="disabled" name="selected_facets" value=',
                                v,
                                '>',
                                '<button id="remove-maintainers-filter"',
                                'class="btn btn-lg p-0 text-danger btn-link"><i class="fa fa-window-close"></i></button>'
                            ].join(' ')
                        );
                    }
                    break;
                case "categories_exact":
                    if (facet_value === "" || sections.length < 2) {
                        $('#c-facets').html("");
                    } else {
                        $('#c-facets').html([
                                'Selected category: <strong>',
                                facet_value,
                                '</strong> <input style="display: none" class="disabled" name="selected_facets" value=',
                                v,
                                '>',
                                '<button id="remove-categories-filter"',
                                'class="btn btn-lg p-0 text-danger btn-link"><i class="fa fa-window-close"></i></button>'
                            ].join(' ')
                        );
                    }
                    break;
                case "variants_exact":
                    if (facet_value === "" || sections.length < 2) {
                        $('#v-facets').html("");
                    } else {
                        $('#v-facets').html([
                                'Selected variant <strong>',
                                facet_value,
                                '</strong> <input style="display: none" class="disabled" name="selected_facets" value=',
                                v,
                                '>',
                                '<button id="remove-variants-filter"',
                                'class="btn btn-lg p-0 text-danger btn-link"><i class="fa fa-window-close"></i></button>'
                            ].join(' ')
                        );
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