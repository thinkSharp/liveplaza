odoo.define('customizations_by_livep.cart', function(require) {
    "use strict";

    var core = require('web.core');
    var config = require('web.config');
    var concurrency = require('web.concurrency');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    var wSaleUtils = require('website_sale.utils');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    require("web.zoomodoo");
    var _t = core._t;
    var Dialog = require('web.Dialog');

    var qweb = core.qweb;

    publicWidget.registry.websiteSaleCart = publicWidget.Widget.extend({
    selector: '.oe_website_sale .oe_cart',
    events: {
        'click .js_change_shipping': '_onClickChangeShipping',
        'click .js_edit_address': '_onClickEditAddress',
        'click .js_delete_product': '_onClickDeleteProduct',
        'click #select-product': '_onClickCheckbox',
        'click #place_order': '_is_checked_products',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onClickChangeShipping: function (ev) {
        var $old = $('.all_shipping').find('.card.border.border-primary');
        $old.find('.btn-ship').toggle();
        $old.addClass('js_change_shipping');
        $old.removeClass('border border-primary');

        var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
        $new.find('.btn-ship').toggle();
        $new.removeClass('js_change_shipping');
        $new.addClass('border border-primary');

        var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
        $.post($form.attr('action'), $form.serialize()+'&xhr=1');
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickEditAddress: function (ev) {
        ev.preventDefault();
        $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address').submit();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickDeleteProduct: function (ev) {
        ev.preventDefault();
        $(ev.currentTarget).closest('tr').find('.js_quantity').val(0).trigger('change');
    },

    _onClickCheckbox: function(ev) {
        var orderID = $(ev.currentTarget).data('order-id');


        ajax.jsonRpc('/shop/checkout/select/products', 'call', {'orderLineId': orderID})
        .then(function(response){
            $(ev.currentTarget).closest('tr').find('.js_quantity').trigger('change');
        });

    },

    _getValue: function() {
        var checkboxes = document.getElementsByName('checked_list');
        var checked_list = 0;

        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) {
                checked_list++;
            }
        }
        return checked_list;
    },

    _is_checked_products: function(ev) {
        if (this._getValue() <= 0) {
            this._displayError(
                _t('No product selected'),
                _t('Please select at least one product')
            )
          return false;
        }
    },

    _displayError: function (title, message) {
        return new Dialog(null, {
            title: _t('Warning: ') + _.str.escapeHTML(title),
            size: 'medium',
            $content: "<p>" + (_.str.escapeHTML(message) || "") + "</p>" ,
            buttons: [
            {text: _t('Ok'), close: true}]}).open();

    },
});
});


