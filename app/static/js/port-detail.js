$(document).ready(function() {
    // Code for Tickets Start
    function loadTickets(port_name) {
        $.ajax({
            type: 'GET',
            url: '/port/' + port_name + '/tickets/',
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

    loadTickets($("#port_name").text());

    $("body").tooltip({ selector: '[data-toggle=tooltip]' });

    $(".loadFiles").click(async function () {
        let id = $(this).attr("id");
        $("#" + id + "-modal").modal('show');
        let build_id = id.split("-")[1];
        const response = await fetch("/api/v1/files/" + build_id + "/");
        const data = await response.json();
        const files = data.files;
        let ul = $("<ul></ul>");
        ul.addClass("list-group");
        for (let i = 0; i < files.length; i++) {
            let li = $("<li></li>");
            li.text(files[i].file);
            li.addClass("list-group-item");
            ul.append(li);
        }
        $("#" + id + "-modal-body").html(ul);
    });
});
