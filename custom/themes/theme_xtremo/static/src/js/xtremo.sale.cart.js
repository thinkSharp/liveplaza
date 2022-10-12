/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('xtremo.sale.price.filter', function (require) {
  "use strict";
  var core = require('web.core');
  var _t = core._t;
  var publicWidget = require('web.public.widget');
  var ajax=require('web.ajax');

  publicWidget.registry.xtremoPriceFilter = publicWidget.Widget.extend({
    selector: "#select_price_range, .modal-body #select_price_range",
    read_events: {
      'submit': '_submitForm',
      'change .xtremo-range-slider': '_setPrice',
      'change .xt-min-price, .xt-max-price': '_manuallySet'
    },
    start: function () {
      this.min = parseInt(this.$target.find(".xt-min-price").attr("value-price"));
      this.max = parseInt(this.$target.find(".xt-max-price").attr("value-price"));
      $('.xtremo-range-slider').jRange({
        from: this.min,
        to: this.max,
        isRange : true,
        showScale : false,
        isRange : false
      });
      this._setPrice();
    },
    _submitForm: function(ev) {
      ev.preventDefault();
      var url = this.$target.attr('action');
      url = url.replace("xtremo-lower-val", this.min).replace("xtremo-higher-val", this.max);
      window.location.href = url;
    },
    _setPrice: function () {
      var price = this.$target.find('.xtremo-range-slider').val().split(",");
      var $el = this.$target.find('.xt-custom-price-range');
      try{
        price = price.map(function(item) {
                    return parseInt(item, 10);
                });
        this.min = Math.min(...price);
        this.max = Math.max(...price);
        $el.find('.xt-min-price').val(this.min);
        $el.find('.xt-max-price').val(this.max);
      }catch (e){
      }
    },
    _manuallySet: function (ev) {
      this.min = this.$target.find(".xt-min-price").val();
      this.max = this.$target.find(".xt-max-price").val();
      var minCheck = parseInt(this.$target.find(".xt-min-price").attr("value-price"));
      var maxCheck = parseInt(this.$target.find(".xt-max-price").attr("value-price"));
      if (parseFloat(this.min) > parseFloat(this.max) || parseFloat(this.min) < parseFloat(minCheck)){
        this.min = minCheck;
        this.$target.find(".xt-min-price").val(minCheck);
      }
      if (parseFloat(this.max) < parseFloat(this.min) || parseFloat(this.max) > parseFloat(maxCheck)){
        this.max = maxCheck;
        this.$target.find(".xt-max-price").val(maxCheck);
      }
      $(".slider-container .back-bar").find(".pointer-label.low").text(this.min);
      $(".slider-container .back-bar").find(".pointer-label.high").text(this.max);
      this.$target.find(".xtremo-range-slider").val(`${this.min},${this.max}`);
    }
  });
});

odoo.define('xtremo.sale.cart', function (require) {
  "use strict";

  var core = require('web.core');
  var _t = core._t;
  var publicWidget = require('web.public.widget');
  var ajax=require('web.ajax');
  var _t = core._t;
  var Dialog = require('web.Dialog');
  var rpc = require('web.rpc');

  publicWidget.registry.websiteSaleCartLink = publicWidget.registry.websiteSaleCartLink.extend({
    selector: '.o_affix_enabled #xtremo_top_menu #my_cart a[href$="/shop/cart"]',
    xmlDependencies: ['/theme_xtremo/static/src/xml/xtremo_dynamic_modal.xml'],
    read_events: {
        'mouseenter': '_onMouseEnter',
        'mouseleave': '_onMouseLeave',
        'click': '_onClick',
//        $('#checkout-modal').on('click', funCheckedProduct);
    },
    start: function () {
      this._super.apply(this);
      var ref = this;
      ref.$target.attr({
        "data-toggle": "tooltip",
        "data-placement": "bottom",
        "title": _t("Show Cart")
      });
      var res = {
        "t_id": "xtremo_cart_modal",
        "t_header": _t("My Shopping Cart"),
//        't_button': `<a role="button" class="btn btn-primary" href="/shop/cart">${ _t("View Cart") }</a>
//                     <a role="button" id="checkout-modal"
//                     class="btn btn-secondary" href="/shop/checkout">${ _t("Checkout") }</a>`
      };
      var html = $(core.qweb.render('theme_xtremo.dynamic_modal', res));
      $('main').append(html);

    },

    _onMouseEnter: function (ev) {
        ev.preventDefault();
        return;
    },

    _onClick: function (ev) {
      var ref = this;
      ev.preventDefault();
      if(window.screen.width <= 767){
        window.location.href = '/shop/cart';
        return;
      }
      ref._callApi(ref, false);
      ev.stopPropagation();
    },

    _callApi: function (ref, refresh) {
      $.get("/shop/cart", {
          type: 'popover',
      }).then(function (data) {
          var $el = $('#xtremo_cart_modal');
          var $cart = $(data);
          if ($cart.hasClass('alert-info')){
            $el.find('.modal-footer').hide();
          }else{
            $el.find('.modal-footer').show();
          }
          $el.find(".modal-body").html($cart);
          $el.modal("show");
          var href = window.location.pathname;
          // $('body').removeClass('modal-open');
          if (["/shop/payment","/shop/checkout"].includes(href)){
            $el.find(".js_delete_product").remove();
          }
          var funDelete = ref._deleteProduct();
          $el.on('click', ".js_delete_product", funDelete);
          var funCheckedProduct = ref._is_checked_products();
          $el.on('click', "#checkout-modal", funCheckedProduct);
          var qty = $el.find('.cart_line:first').length > 0 ? $el.find('.cart_line:first').attr('cart_qty') : 0;
//          $("#xtremo_top_menu #my_cart .my_cart_quantity").text(qty);
      });
    },

    _deleteProduct: function () {
      var ref = this;
      return function (ev) {
        var $el = ev.currentTarget;
        ajax.jsonRpc("/shop/cart/update_json", 'call', {
          'line_id': parseInt($el.getAttribute("line")),
          'product_id': parseInt($el.getAttribute("pline")),
          'set_qty': 0
        }).then(function (data) {
          ref._callApi(ref, true);
          if (window.location.pathname.includes("/shop/cart")){
            $(`table input[data-line-id="${$el.getAttribute('line')}"][class^="js_quantity"]`).val(0).trigger('change');
          }
          ev.stopPropagation();
        })
      }
    },

    _is_checked_products: function() {
       return function(ev){
            var order_len = $(ev.currentTarget).data('order-length');

            if(order_len <= 0) {
               displayError(
                    _t('No product selected'),
                    _t('Go to Cart and select at least one product')
                );
                return false;
            }
       }

       function displayError(title, message) {
            return new Dialog(null, {
                title: _t('Warning: ') + _.str.escapeHTML(title),
                size: 'medium',
                $content: "<p>" + (_.str.escapeHTML(message) || "") + "</p>" ,
                buttons: [
                {text: _t('Ok'), close: true}]}).open();
           }
    },

  });

});

odoo.define('do_customization.buy_again', function (require) {
"use strict";

    var publicWidget = require('web.public.widget');
    var wSaleUtils = require('website_sale.utils');

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
            e.preventDefault();
            var $navButton = wSaleUtils.getNavBarButton('.o_wsale_my_cart');
//            var tr = $(e.currentTarget).parents('tr');
            var tr = $(e.currentTarget).parents('.ordered_product');
            var product = tr.data('product-id');
            $('.o_wsale_my_cart').removeClass('d-none');
            wSaleUtils.animateClone($navButton, tr, 25, 850);

            return this._addToCart(product, tr.find('add_qty').val() || 1);

        },

    })
});

odoo.define('do_customization.product_tracking_modal', function (require) {
"use strict";

    var publicWidget = require('web.public.widget');
    var ajax=require('web.ajax');

    publicWidget.registry.ProductTrackingModal = publicWidget.Widget.extend({
        selector: '.order_details_outer',
        events: {
            'click #product_tracking_btn': '_callModal',
        },

        _callModal: function(e) {
            var tr = $(e.currentTarget).parents('tr');
            var line = tr.data('order-line');
            var append_div = $('#product_tracking_modal');
            ajax.jsonRpc("/orders/order_line/delivery_tracking/modal", 'call', {
                'line_id': parseInt(line)
            }).then(function(modal){
                var $modal = $(modal);
                $modal.appendTo(append_div)
                    .modal('show')
            });
        },



    })
});

odoo.define('do_customization.payment_ss_edit', function (require) {
"use strict";

    var publicWidget = require('web.public.widget');
    var ajax=require('web.ajax');

    publicWidget.registry.PaymentSSEdit = publicWidget.Widget.extend({
        selector: '.order_details_outer',
        events: {
            'click #edit_ss_btn': '_callModal',
            'click #ss_img': '_callViewModal',
        },

        _callModal: function(e) {
            var tr = $(e.currentTarget).parents('.payment_ss_editor');
            var order = tr.data('order-id');
            var append_div = $('#payment_ss_edit_modal');
            ajax.jsonRpc("/my/orders/payment/edit_modal", 'call', {
                'sale_order_id': parseInt(order)
            }).then(function(modal){
                var $modal = $(modal);
                $modal.appendTo(append_div)
                    .modal('show')
            });
        },

        _callViewModal: function(e) {
            var tr = $(e.currentTarget).parents('.payment_ss_editor');
            var order = tr.data('order-id');
            var append_div = $('#payment_ss_view_modal');
            ajax.jsonRpc("/my/orders/payment/view_modal", 'call', {
                'sale_order_id': parseInt(order)
            }).then(function(modal){
                var $modal = $(modal);
                $modal.appendTo(append_div)
                    .modal('show')
            });
        },
    })
});
