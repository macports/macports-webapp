$(function () {
    $('#search').ready(function () {
        $.ajax({
            type: 'POST',
            url: '/ports/load_tickets/',
            data: {
                'portname': $('#port_name').text(),
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: showTickets,
            beforeSend: function() {
                $('#trac_tickets').html("Loading Tickets From Trac ...")
            },
            dataType: 'html'
        });
    });
});

function showTickets(data, textStatus, jqXHR) {
    $('#trac_tickets').html(data);
}