odoo.define('website_stock.website_stock_main', function(require) {
    "use strict";

    $(document).ready(function() { 
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;

            var $js_quantity = $(this).find('.css_quantity.input-group.oe_website_spinner');
            website_stock_main($js_quantity);
            $(oe_website_sale).on('change', function(ev) {
                website_stock_main($js_quantity);
            });
        });

        function website_stock_main($js_quantity) {
            if ($("input[name='product_id']").is(':radio'))
                var product = $("input[name='product_id']:checked").attr('value');
            else
                var product = $("input[name='product_id']").attr('value');
            var value = $('#' + product).attr('value');
            var allow = $('#' + product).attr('allow');
            $('.stock_info_div').hide();
            $('#' + product).show();
            if (value <= 0 && allow === 'deny') {
                $('#add_to_cart').hide();
                $js_quantity.hide();
            } else {
                $('#add_to_cart').show();
                $js_quantity.show();
            }
        }
    });
});


/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* Responsible Developer:- Sunny Kumar Yadav */