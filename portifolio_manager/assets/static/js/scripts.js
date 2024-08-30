$(document).ready(function() {
    $('#id_ticker_type').change(function() {
        var url = ajaxUrl  // URL to the view that handles the AJAX request
        var tickerTypeId = $(this).val();  // get the selected ticker type
        $.ajax({
            url: url,
            method: 'GET',
            data: {
                'ticker_type': tickerTypeId
            },
            success: function(data) {
                var $tickerCodeSelect = $("#id_ticker_code");
                $tickerCodeSelect.empty();  // Clear the existing options
                $tickerCodeSelect.append('<option value="">Selecione o Ticker</option>');  // Add a default option
                $.each(data, function(index, item) {
                    $tickerCodeSelect.append('<option value="' + item.id + '">' + item.ticker + '</option>');
                });
            }
        });
    });
});

window.addEventListener('resize', function() {
    Plotly.Plots.resize(document.getElementById('graph_div'));
});