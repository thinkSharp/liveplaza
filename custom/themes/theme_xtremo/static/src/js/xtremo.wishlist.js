odoo.define('xtremo.wishlist', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');
var VariantMixin = require('sale.VariantMixin');
var old_wishlist = require('website_sale_wishlist.wishlist');
var utils = require('web.utils');
var session = require('web.session');
var wishlist = publicWidget.registry.ProductWishlist;

    $(document).ready(function() {
        updateWishlistView();
     });

     function updateWishlistView () {
        var user = (session.user_id);
        var user_str = user.toString();
        if(user == false) {
            user_str = "guest";
        }
        if(utils.get_cookie(user_str) == null) {
            utils.set_cookie(user_str,  '[]');
        }
        var wishlist_products = JSON.parse(utils.get_cookie(user_str) || "[]");
        var sup = $("#my_wish sup");
        if (wishlist_products.length >= 0) {
            $('.o_wsale_my_wish').show();
            $('.my_wish_quantity').text(wishlist_products.length);
        } else {
            $('.o_wsale_my_wish').hide();
        }
    }

// VariantMixin events are overridden on purpose here
// to avoid registering them more than once since they are already registered
// in website_sale.js
publicWidget.registry.ProductWishlist = publicWidget.Widget.extend(VariantMixin, {
    selector: '.oe_website_sale',
    events: {
        'click .o_wsale_my_wish': '_onClickMyWish',
        'click .o_add_wishlist, .o_add_wishlist_dyn': '_onClickAddWish',
        'change input.product_id': '_onChangeVariant',
        'change input.js_product_change': '_onChangeProduct',
        'click .wishlist-section .o_wish_rm': '_onClickWishRemove',
        'click .wishlist-section .o_wish_add': '_onClickWishAdd',
    },

    /**
     * @constructor
     */
    init: function (parent) {
        this._super.apply(this, arguments);
        this.wishlistProductIDs = [];

        utils.set_cookie("guest", '[]');

        this.guest_wishlist = [];

    },
    /**
     * Gets the current wishlist items.
     * In editable mode, do nothing instead.
     *
     * @override
     */
    willStart: function () {
        var self = this;
        var def = this._super.apply(this, arguments);

        var wishDef = $.get('/shop/wishlist', {
            count: 1,
        }).then(function (res) {
            self.wishlistProductIDs = JSON.parse(res);
        });
        return Promise.all([def, wishDef]);
    },
    /**
     * Updates the wishlist view (navbar) & the wishlist button (product page).
     * In editable mode, do nothing instead.
     *
     * @override
     */
    start: function () {
        var user = session.user_id.toString();
        var wishlist_products = JSON.parse(utils.get_cookie(session.user_id.toString()) || "[]");
        var def = this._super.apply(this, arguments);
        this._updateWishlistView();
        // trigger change on only one input
        if (this.$('input.js_product_change').length) { // manage "List View of variants"
            this.$('input.js_product_change:checked').first().trigger('change');
        } else {
            this.$('input.product_id').first().trigger('change');
        }

        return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _addNewProducts: function ($el) {
        var self = this;
        var productID = $el.data('product-product-id');
        if ($el.hasClass('o_add_wishlist_dyn')) {
            productID = $el.parent().find('.product_id').val();
            if (!productID) { // case List View Variants
                productID = $el.parent().find('input:checked').first().val();
            }
            productID = parseInt(productID, 10);
        }
        var $form = $el.closest('form');
        var templateId = $form.find('.product_template_id').val();
        // when adding from /shop instead of the product page, need another selector
        if (!templateId) {
            templateId = $el.data('product-template-id');
        }
        $el.prop("disabled", true).addClass('disabled');
        var productReady = this.selectOrCreateProduct(
            $el.closest('form'),
            productID,
            templateId,
            false
        );

        productReady.then(function (productId) {
            productId = parseInt(productId, 10);
            if(session.user_id != false) {

                if (productId && !_.contains(self.wishlistProductIDs, productId)) {
                    return self._rpc({
                        route: '/shop/wishlist/add',
                        params: {
                            product_id: productId,
                        },
                    }).then(function () {
                        var $navButton = wSaleUtils.getNavBarButton('#my_wish');
                        self.wishlistProductIDs.push(productId);
                        utils.set_cookie((session.user_id).toString(), "", -1);
                        utils.set_cookie((session.user_id).toString(), JSON.stringify(self.wishlistProductIDs), false);
                        self._updateWishlistView();
                        wSaleUtils.animateClone($navButton, $el.closest('form'), 0, 0);
                    }).guardedCatch(function () {
                        $el.prop("disabled", false).removeClass('disabled');
                    });
                }
            }
            else {
                if (productId && !_.contains(self.guest_wishlist, productId)) {

                    return self._rpc({
                        route: '/shop/wishlist/add',
                        params: {
                            product_id: productId,
                        },
                    }).then(function () {
                        var $navButton = wSaleUtils.getNavBarButton('#my_wish');
                        self.guest_wishlist.push(productId);
                        utils.set_cookie("guest", "", -1);
                        utils.set_cookie("guest", JSON.stringify(self.guest_wishlist), false);
                        self._updateWishlistView();
                        wSaleUtils.animateClone($navButton, $el.closest('form'), 0, 0);
                    }).guardedCatch(function () {
                        $el.prop("disabled", false).removeClass('disabled');
                    });
                }
            }
        });
    },
    /**
     * @private
     */

    _updateWishlistView: function () {
        var guest_products = JSON.parse(utils.get_cookie("guest") || "[]");
        var user_products = JSON.parse(utils.get_cookie(session.user_id.toString()) || "[]");
        if(session.user_id == false) {
            if (this.guest_wishlist.length >= 0) {
                $('.o_wsale_my_wish').show();
                $('.my_wish_quantity').text(this.guest_wishlist.length);
            } else {
                $('.o_wsale_my_wish').hide();
            }
        }
        else {
            if (this.wishlistProductIDs.length >= 0) {
                $('.o_wsale_my_wish').show();
                $('.my_wish_quantity').text(this.wishlistProductIDs.length);
            } else {
                $('.o_wsale_my_wish').hide();
            }
        }
    },
    /**
     * @private
     */

    _removeWish: function (e, deferred_redirect) {
        var tr = $(e.currentTarget).parents('tr');
        var wish = tr.data('wish-id');
        var product = tr.data('product-id');
        var self = this;

        this._rpc({
            route: '/shop/wishlist/remove/' + wish,
        }).then(function () {
            $(tr).hide();
        });

        if(session.user_id == false){
            this.guest_wishlist = _.without(this.guest_wishlist, product);
            utils.set_cookie("guest", JSON.stringify(self.guest_wishlist), false);
            if (this.guest_wishlist.length === 0) {
                if (deferred_redirect) {
                    deferred_redirect.then(function () {
                        self._redirectNoWish();
                    });
                }
            }
        }
        else {
            this.wishlistProductIDs = _.without(this.wishlistProductIDs, product);
            utils.set_cookie((session.user_id).toString(), JSON.stringify(self.wishlistProductIDs), false);
            if (this.wishlistProductIDs.length === 0) {
                if (deferred_redirect) {
                    deferred_redirect.then(function () {
                        self._redirectNoWish();
                    });
                }
            }
        }


        this._updateWishlistView();
    },
    /**
     * @private
     */
    _addOrMoveWish: function (e) {
        var $navButton = wSaleUtils.getNavBarButton('.o_wsale_my_cart');
        var tr = $(e.currentTarget).parents('tr');
        var product = tr.data('product-id');
        $('.o_wsale_my_cart').removeClass('d-none');
        wSaleUtils.animateClone($navButton, tr, 25, 40);

        if ($('#b2b_wish').is(':checked')) {
            return this._addToCart(product, tr.find('add_qty').val() || 1);
        } else {
            var adding_deffered = this._addToCart(product, tr.find('add_qty').val() || 1);
            this._removeWish(e, adding_deffered);
            return adding_deffered;
        }
    },
    /**
     * @private
     */
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
    /**
     * @private
     */
    _redirectNoWish: function () {
        window.location.href = '/shop/cart';
    },


    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickMyWish: function () {
        if(session.user_id == false) {
            utils.set_cookie("guest", JSON.stringify(self.guest_wishlist), false);
            if (this.guest_wishlist.length === 0) {
                this._updateWishlistView();
                this._redirectNoWish();
                return;
            }
        }
        else {
            utils.set_cookie((session.user_id).toString(), JSON.stringify(self.wishlistProductIDs), false);
            if (this.wishlistProductIDs.length === 0) {
                this._updateWishlistView();
                this._redirectNoWish();
                return;
            }
        }
        window.location = '/shop/wishlist';
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickAddWish: function (ev) {
        this._addNewProducts($(ev.currentTarget));
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onChangeVariant: function (ev) {
        var $input = $(ev.target);
        var $parent = $input.closest('.js_product');
        var $el = $parent.find("[data-action='o_wishlist']");
        if(session.user_id == false) {
            if (!_.contains(this.guest_wishlist, parseInt($input.val(), 10))) {
                $el.prop("disabled", false).removeClass('disabled').removeAttr('disabled');
            } else {
                $el.prop("disabled", true).addClass('disabled').attr('disabled', 'disabled');
            }
        }
        else {
            if (!_.contains(this.wishlistProductIDs, parseInt($input.val(), 10))) {
                $el.prop("disabled", false).removeClass('disabled').removeAttr('disabled');
            } else {
                $el.prop("disabled", true).addClass('disabled').attr('disabled', 'disabled');
            }
        }
        $el.data('product-product-id', parseInt($input.val(), 10));
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onChangeProduct: function (ev) {
        var productID = ev.currentTarget.value;
        var $el = $(ev.target).closest('.js_add_cart_variants').find("[data-action='o_wishlist']");
        if(session.user_id == false) {
            if (!_.contains(this.guest_wishlist, parseInt(productID, 10))) {
                $el.prop("disabled", false).removeClass('disabled').removeAttr('disabled');
            } else {
                $el.prop("disabled", true).addClass('disabled').attr('disabled', 'disabled');
            }
        }
        else {
            if (!_.contains(this.wishlistProductIDs, parseInt(productID, 10))) {
                $el.prop("disabled", false).removeClass('disabled').removeAttr('disabled');
            } else {
                $el.prop("disabled", true).addClass('disabled').attr('disabled', 'disabled');
            }
        }
        $el.data('product-product-id', productID);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickWishRemove: function (ev) {
        this._removeWish(ev, false);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickWishAdd: function (ev) {
        var self = this;
        this.$('.wishlist-section .o_wish_add').addClass('disabled');
        this._addOrMoveWish(ev).then(function () {
            self.$('.wishlist-section .o_wish_add').removeClass('disabled');
        });
    },
});
});

