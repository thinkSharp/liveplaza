odoo.define('payment_wavepay.payment_wavepay', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');

    var qweb = core.qweb;
    var _t = core._t;

    if ($.blockUI) {
        $.blockUI.defaults.css.border = '0';
        $.blockUI.defaults.css["background-color"] = '';
        $.blockUI.defaults.overlayCSS["opacity"] = '0.5';
        $.blockUI.defaults.overlayCSS["z-index"] = '1050';
    }

    var WavePayPaymentForm = Widget.extend({
        init: function() {
            this.tx_id = $('#wavepay_tx').val();
            this.secret_Id = $('#secret_Id').val();
            this.merchant_Id = $('#merchant_Id').val();

            this.start();
            this._initBlockUI(_t("Loading..."));
            
        },
        start: function() {
            var self = this;
            self._createWavePayToken();
        },
        _createWavePayToken: function() {
            var self = this;
            ajax.jsonRpc('/payment/wavepay/token/create', 'call', {
                'txId': self.tx_id,
            })
            .then(function (res) {
                if (res) {
                    var data = JSON.parse(res);
                    if ("url" in data) {
                        window.location.href = data['url'];
                    } else {
                        self._showErrorMessage(_t('WavePay Payment Error'), data['message']);
                    }
                } else {
                    self._showErrorMessage(_t('WavePay Payment Error'), "Error in Python");
                }
            });
        },
        _showErrorMessage: function(title, message) {
            this._revokeBlockUI();
            $("#o_payment_form_pay").hide();
            return new Dialog(null, {
                title: _t('Error: ') + _.str.escapeHTML(title),
                size: 'medium',
                $content: "<p>" + (_.str.escapeHTML(message) || "") + "</p>" ,
                buttons: [
                {text: _t('Ok'), close: true}]}).open();
        },
        _revokeBlockUI: function() {
            if ($.blockUI) {
                $.unblockUI();
            }
            $("#o_payment_form_pay").removeAttr('disabled');
        },
        _initBlockUI: function(message) {
            if ($.blockUI) {
                $.blockUI({
                    'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                            '    <br />' + message +
                            '</h2>'
                });
            }
            $("#o_payment_form_pay").attr('disabled', 'disabled');
        },

    });

    new WavePayPaymentForm();

});
