$(function($) {
    $('#id_dukandaar').on('change', function() {
        var dukandaarId = $(this).val();
        var billDropdown = $('#id_bill');
        console.log("ya")
        if (!dukandaarId) {
            billDropdown.html('<option value="">Select a bill</option>');
            return;
        }
        console.log(dukandaarId)
        $.ajax({
            url: '/get_unpaid_bills/',  // URL to fetch unpaid bills
            data: {
                'dukandaar': dukandaarId
            },
            success: function(data) {
                console.log(data);
                var options = '<option value="">Select a bill</option>';
                data.bills.forEach(function(bill) {
                    options += '<option value="' + bill.id + '">' + bill.__str__ + '</option>';
                });
                billDropdown.html(options);
            }
        });
    });
});
