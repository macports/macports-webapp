// Code for Tickets Start
function loadTickets(port_name) {
    $.ajax({
        type: 'GET',
        url: '/port/' + port_name + '/tickets',
        data: {
            'port_name': port_name,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: receiveTickets,
        beforeSend: function () {
            $('#tickets-box').html("Please wait while tickets are fetched from Trac");
        },
        dataType: 'html'
    });
}

function receiveTickets(data, textStatus, jqXHR) {
    $('#tickets-box').html(data);
    var count = $('#tickets-count-returned').text();
    $('#tickets-count').html(count);
}

// Mouse over for closed maintainer
$(document).ready(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});
