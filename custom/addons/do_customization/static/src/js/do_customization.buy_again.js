odoo.define('do_customization.buy_again', function (require) {
"use strict";

    var publicWidget = require('web.public.widget');
    var wSaleUtils = require('website_sale.utils');

//    $(document).ready(function() {
//        alert("buy ready");
//     });

    publicWidget.registry.BuyAgain = publicWidget.Widget.extend({
        selector: '.orders_container',
        events: {
            'click #buy-again': '_buyAgain',
            'click #buy-again2': '_buyAgain',
        },

        _addToCart: function (productID, qty_id) {
            return this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    product_id: parseInt(productID, 10),
                    add_qty: parseInt(qty_id, 10),
                    display: false,
                },
            }).then(function (resp) {
                if (resp.warning) {
                    if (! $('#data_warning').length) {
                        $('.wishlist-section').prepend('<div class="mt16 alert alert-danger alert-dismissable" role="alert" id="data_warning"></div>');
                    }
                    var cart_alert = $('.wishlist-section').parent().find('#data_warning');
                    cart_alert.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + resp.warning);
                }
                $('.my_cart_quantity').html(resp.cart_quantity || '<i class="fa fa-warning" /> ');
            });
        },

        _buyAgain: function (e) {
            var $navButton = wSaleUtils.getNavBarButton('.o_wsale_my_cart');
            var tr = $(e.currentTarget).parents('tr');
            var product = tr.data('product-id');
            $('.o_wsale_my_cart').removeClass('d-none');
            wSaleUtils.animateClone($navButton, tr, 25, 40);

            return this._addToCart(product, tr.find('add_qty').val() || 1);

        },

    })
});