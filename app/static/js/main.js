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

function BasicSort(a, b) {
    let a_segments = a.label.split(".");
    let a_l = a_segments.length;
    let b_segments = b.label.split(".");
    let b_l = b_segments.length;
    let i = 0;
    while (i < a_l && i < b_l) {
        let a = a_segments[i];
        let b = b_segments[i];
        i++;
        // If both segments are numbers
        if (!isNaN(a) && !isNaN(b)) {
            if (parseInt(a) > parseInt(b))
                return 1;
            else if (parseInt(a) < parseInt(b))
                return -1;
            else
                continue;
        }

        // If a is number, and b is not, a wins
        if (!isNaN(a))
            return 1;

        // If b is numeric, and a is not, b wins
        if (!isNaN(b))
            return -1;

        // If none is numeric, use Javascript's string comparator
        if (a > b)
            return 1;
        if (b > a)
            return -1;
    }
    // If i is equal to the length of both, then they are equal
    if (i == a_l && i == b_l)
        return 0;

    if (a_l > b_l)
        return 1;
    else
        return -1;
}

function getColors(length) {
    let pallet = ["#0074D9", "#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA", "#7979ea", "#548e7d", "#53cc4d", "#e5ae22", "#3ecbd8"];
    let colors = [];

    for (let i = 0; i < length; i++) {
        colors.push(pallet[i % pallet.length]);
    }

    return colors;
}
