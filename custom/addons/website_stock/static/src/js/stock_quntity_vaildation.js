

odoo.define('website_stock.stock_quntity_vaildation', function(require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');

    var _t = core._t;
    var temp = '1';
//    var old_qty = '1';

    $(document).ready(function() {

        $('.oe_website_sale').each(function() {

            var oe_website_sale = this;

            $(oe_website_sale).on("change", ".oe_cart input.js_quantity", function(ev) {
                var $input = $(this);
                var value = parseInt($input.val(), 10);
                var $dom = $(this).closest('tr');
                var line_id = parseInt($input.data('line-id'), 10);
                var product_id = parseInt($input.data('product-id'), 10);
                var old_qty = parseInt($input.data('old-qty'));
                if (isNaN(value)) {
                    $input.val(old_qty);
                }

                ajax.jsonRpc("/shop/cart/update_json/msg", 'call', {
                    'line_id': line_id,
                    'product_id': parseInt($input.data('product-id'), 10),
                    'set_qty': value
                })
                .then(function(msg) {
                    if (msg) {
                        $input.val(old_qty);
                        $dom.popover({
                            content: _t("You are Trying to Add More Than Available Quantity of Product."),
                            title: _t("WARNING"),
                            placement: "top",
                            trigger: 'focus',
                        });
                        $dom.popover('show');
                        setTimeout(function() {
                            $dom.popover('dispose')
                        }, 1000);

                    } else {
                        $dom.popover('dispose');
                    }
                });
            });

            // function for '/shop/product' page product quantity vailidation on click of add to cart button
            $(oe_website_sale).on("click", '#add_to_cart', function(ev) {
                var $form = $(this).closest('form');
                if ($("input[name='product_id']").is(':radio'))
                    var product_id = $("input[name='product_id']:checked").attr('value');
                else
                    var product_id = $("input[name='product_id']").attr('value');
                var add_qty = parseFloat($form.find('input[type="text"][name="add_qty"]').first().val(), 10);

                ajax.jsonRpc("/shop/cart/update/msg", 'call', {
                    'product_id': product_id,
                    'add_qty': add_qty
                })
                .then(function(result) {
                    if (result.status == 'deny') {
                        $form.find('input[type="text"][name="add_qty"]').first().val(temp);
                        $('#add_to_cart').popover({
                            content: _t("You Already Added All Avalible Quantity of Product in Your Cart, You Can not Add More Quantity."),
                            title: _t("WARNING"),
                            placement: "left",
                            trigger: 'focus',
                        });
                        $('#add_to_cart').popover('show');
                        setTimeout(function() {
                            $('#add_to_cart').popover('dispose')
                        }, 1000);

                    } else {
                        $('#add_to_cart').popover('dispose');
                        temp = add_qty.toString();
                    }
                });
            });

            // function for '/shop/product' page product quantity vailidation on increment of product quantity
            $(oe_website_sale).find('input[type="text"][name="add_qty"]').on('change', function(ev) {
                var $form = $(this).closest('form');
                if ($("input[name='product_id']").is(':radio'))
                    var product_id = $("input[name='product_id']:checked").attr('value');
                else
                    var product_id = $("input[name='product_id']").attr('value');
                var add_qty = parseFloat($form.find('input[type="text"][name="add_qty"]').first().val(), 10);
                ajax.jsonRpc("/shop/cart/update/msg", 'call', {
                    'product_id': product_id,
                    'add_qty': add_qty
                })
                .then(function(result) {
                    if (result.status == 'deny') {
                        $form.find('input[type="text"][name="add_qty"]').first().val(temp);
                        $('.css_quantity').popover({
                            content: _t("You Can Not Add More Quantity."),
                            title: _t("WARNING"),
                            placement: "top",
                            trigger: 'focus',
                        });
                        $('.css_quantity').popover('show');
                        setTimeout(function() {
                            $('.css_quantity').popover('dispose')
                        }, 1000);
                    } else {
                        $('.css_quantity').popover('dispose');
                        temp = add_qty.toString();
                    }
                });
            });

            $(oe_website_sale).on('click', 'a.btn.btn-default.btn-xs', function(ev) {
                var $form = $(this).closest('form');
                var $msg = $form.find('.fa-shopping-cart');
                var product_id = parseInt($form.find('input[type="hidden"][name="product_id"]').first().val(), 10);
                ajax.jsonRpc("/shop/cart/update/msg", 'call', {
                    'product_id': product_id,
                    'add_qty': 1
                })
                .then(function(result) {
                    if (result.status == 'deny') {
                        $(this).addClass('disabled');
                        alert(_t("You Can Not Add This Product in Your Cart."))
                    }
                });
            });
        });
    });
});


/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* Responsible Developer:- Sunny Kumar Yadav */