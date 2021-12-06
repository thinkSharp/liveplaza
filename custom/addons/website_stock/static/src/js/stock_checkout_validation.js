odoo.define('website_stock.stock_checkout_validation', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {    
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;

            $(oe_website_sale).on('click', '.remove-cart-line', function() {
                var $dom = $(this).closest('td');
                var line_id = parseInt($dom.data('line-id'), 10);
                var product_id = parseInt($dom.data('product-id'), 10);
                ajax.jsonRpc("/shop/cart/update_json", 'call', {
                    'line_id': line_id,
                    'product_id': product_id,
                    'set_qty': 0.0
                })
                .then(function(data) {
                    var $q = $(".my_cart_quantity");
                    $q.parent().parent().removeClass("hidden", !data.quantity);
                    $q.html(data.cart_quantity).hide().fadeIn(600);
                    location.reload();
                });
            });
            
        });
    });
});


/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* Responsible Developer:- Sunny Kumar Yadav */