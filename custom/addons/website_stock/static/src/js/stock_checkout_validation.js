console.log("stock")

odoo.define('website_stock.stock_checkout_validation', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {    
//        $('.oe_website_sale').each(function() {
//            console.log("hay I am here")
//            var oe_website_sale = this;
//            console.log("EEE")
//            console.log(oe_website_sale)
//            $(oe_website_sale).on('click', '.remove-cart-line', function() {
//                var $dom = $(this).closest('td');
//                var line_id = parseInt($dom.data('line-id'), 10);
//                var product_id = parseInt($dom.data('product-id'), 10);
//                console.log("line_id");
//                console.log(line_id);
//
//                console.log("product_id");
//                console.log(product_id)
//                ajax.jsonRpc("/shop/cart/update_json", 'call', {
//                    'line_id': line_id,
//                    'product_id': product_id,
//                    'set_qty': 0.0
//                })
//                .then(function(data) {
//                    var $q = $(".my_cart_quantity");
//                    $q.parent().parent().removeClass("hidden", !data.quantity);
//                    $q.html(data.cart_quantity).hide().fadeIn(600);
//                    location.reload();
//                });
//            });
//
//        });
    });
});


/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* Responsible Developer:- Sunny Kumar Yadav */