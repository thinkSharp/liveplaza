odoo.define('shipping_per_product.checkout', function (require) {
'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    require('website_sale_delivery.checkout');
    var PaymentForm = require('do_customization.payment_next');

    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    publicWidget.registry.websiteSaleDelivery.include({
        events: _.defaults({
            "click .sol_delivery_carrier input[name^='delivery_type']" : '_onSOLCarrierClick',
        }, publicWidget.registry.websiteSaleDelivery.events),

        init: function(){
            this._super.apply(this, arguments);
            this.del_div = false;
        },


        start: function () {
            var self = this;
            var $carriers = $('#delivery_carrier input[name="delivery_type"]');
            var $payButton = $('#o_payment_form_next');
            // Workaround to:
            // - update the amount/error on the label at first rendering
            // - prevent clicking on 'Pay Now' if the shipper rating fails
            if ($carriers.length > 0) {
                if ($carriers.filter(':checked').length === 0) {
                    $payButton.prop('disabled', true);
                    $payButton.data('disabled_reasons', $payButton.data('disabled_reasons') || {});
                    $payButton.data('disabled_reasons').carrier_selection = true;
                }
                $carriers.filter(':checked').click();
            }

            // Asynchronously retrieve every carrier price
            _.each($carriers, function (carrierInput, k) {
                self._showLoading($(carrierInput));
                self._rpc({
                    route: '/shop/carrier_rate_shipment',
                    params: {
                        'carrier_id': carrierInput.value,
                    },
                }).then(self._handleCarrierUpdateResultBadge.bind(self));
            });

            return this._super.apply(this, arguments);
        },

        _handleCarrierUpdateResult: function (result) {
            this._handleCarrierUpdateResultBadge(result);
            var $payButton = $('#o_payment_form_next');
            var $amountDelivery = $('#order_delivery .monetary_field');
            var $amountUntaxed = $('#order_total_untaxed .monetary_field');
            var $amountTax = $('#order_total_taxes .monetary_field');
            var $amountTotal = $('#order_total .monetary_field');

            if (result.status === true) {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
                $payButton.data('disabled_reasons').carrier_selection = false;
                $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
            } else {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
            }
        },

        _handleCarrierUpdateResultBadge: function (result) {
            var $carrierBadge = this.del_div.find('input[name^="delivery_type"][value=' + result.carrier_id + '] ~ .o_wsale_delivery_badge_price');
            var $check_sol_del = this.del_div.find('input[name^="line_delivery_name"]');

            if (result.status === true) {
                 // if free delivery (`free_over` field), show 'Free', not '$0'
                 if (result.is_free_delivery) {
                     $carrierBadge.text(_t('Free'));
                 } else {
                     $carrierBadge.html(result.sol_delivery_amount);
                 }
                 $carrierBadge.removeClass('o_wsale_delivery_carrier_error');
                 $check_sol_del.val("SOL Delivery Selected");
            } else {
                $carrierBadge.addClass('o_wsale_delivery_carrier_error');
                $carrierBadge.text(result.error_message);
                $check_sol_del.val("");
            }
        },

        _onSOLCarrierClick: function(ev){
            var $this = $(ev.currentTarget);
            var self = this;
            var $payButton = $('#o_payment_form_next');
            $payButton.prop('disabled', true);
            $payButton.data('disabled_reasons', $payButton.data('disabled_reasons') || {});
            $payButton.data('disabled_reasons').carrier_selection = true;
            var del_div = $this.closest('.sol_delivery_carrier');
            this.del_div = del_div;
            var carrier_id = $this.val();
            var sol_ids = del_div.find('.sale_order_line_id').data('sale_order_line_ids');
            var $empty_sol_del_error = del_div.find('.empty_sol_del_error');
            var values = {'carrier_id': carrier_id, 'order_lines': sol_ids};
            $empty_sol_del_error.hide();
            dp.add(this._rpc({
                route: '/shop/sol/update_carrier',
                params: values,
            })).then(this._handleCarrierUpdateResult.bind(this));
        },
    });

    PaymentForm.include({

        _checkSolDelivery: function(event){
            var count = 1
            $('.line_delivery_name').each(function () {
                var $this = $(this);
                var $empty_sol_del_error = $this.closest('.sol_delivery_carrier').find('.empty_sol_del_error');
                if($(this).val() == ''){
                    count = 0;
                    $empty_sol_del_error.show();
                    try{
                        var thead = $empty_sol_del_error.closest('table');
                        $("html, body").animate({ scrollTop: thead.offset().top }, 500);
                    }
                    catch(err) {
                        console.log("Error:-",err.message);
                    }
                    setTimeout(function() {$empty_sol_del_error.hide()},12000);
                    return false;
                }
            });
            return count;
        },
//        payEvent: function (ev) {
//            ev.preventDefault();
//            var result = this._checkSolDelivery();
//            if(result == 1){
//                this._super.apply(this, arguments);
//            }
//        }
    });
});
