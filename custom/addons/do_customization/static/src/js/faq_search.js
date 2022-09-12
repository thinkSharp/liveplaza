
odoo.define('do_customization.faq.search', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');

    publicWidget.registry.faqSearch = publicWidget.Widget.extend({
    selector: '#faq-search',
    events: {
//      'keypress input[type="text"]': '_pressEnterKey',
//      'mouseenter .input-group-append button': '_mouseenter'
        'click .faq_search_btn': '_search',
    },

    start: function () {
      var textBox = $("#faq-search input[type='text']");
//      var searchMobile = $("#xtremo_mobile_menu .col-sm-12 .fa-search");
      textBox.on('keypress', this._getSearch);
    },

    _search: function () {
      var $target = this.$target;
      var searchString = $target.find("input[type='text']").val();
      if (searchString.length > 0){
        let url = `/faq?search=${searchString}`;

        window.location.href = url;
//        document.getElementById("faq-search-box").value = searchString;
      }
      else {
        let url = '/faq'
        window.location.href = url;
      }
    },

    _getSearch: function (ev) {
      var bool = ev.currentTarget.classList.contains("fa-search");
      var searchString = "";
      if (bool) {
        var searchString = $("#faq-search input[type='text']").val();
      } else if (ev.keyCode === 13) {
        var searchString = ev.currentTarget.value;
      }
      if (searchString.length > 0){
        window.location.href = `/faq?search=${searchString}`;
      }
    },

  });

});

odoo.define('do_customization.payment_next', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');

var _t = core._t;

publicWidget.registry.Payment = publicWidget.Widget.extend({
    selector: '.o_payment_next_form',
    events: {
        'submit': 'onSubmit',
        'click #o_payment_form_next': 'payEvent',
        'click #o_payment_form_add_pm': 'addPmEvent',
        'click button[name="delete_pm"]': 'deletePmEvent',
        'click .o_payment_form_pay_icon_more': 'onClickMorePaymentIcon',
        'click .o_payment_acquirer_select': 'radioClickEvent',
    },

    /**
     * @override
     */
    start: function () {
        if(!$('#checkbox_cgv').length){
            $("#o_payment_form_pay").removeAttr('disabled');
        }
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.options = _.extend(self.$el.data(), self.options);
            self.updateNewPaymentDisplayStatus();
            $('[data-toggle="tooltip"]').tooltip();
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {string} title
     * @param {string} message
     */
    displayError: function (title, message) {
        var $checkedRadio = this.$('input[type="radio"]:checked'),
            acquirerID = this.getAcquirerIdFromRadio($checkedRadio[0]);
        var $acquirerForm;
        if (this.isNewPaymentRadio($checkedRadio[0])) {
            $acquirerForm = this.$('#o_payment_add_token_acq_' + acquirerID);
        }
        else if (this.isFormPaymentRadio($checkedRadio[0])) {
            $acquirerForm = this.$('#o_payment_form_acq_' + acquirerID);
        }

        if ($checkedRadio.length === 0) {
            return new Dialog(null, {
                title: _t('Error: ') + _.str.escapeHTML(title),
                size: 'medium',
                $content: "<p>" + (_.str.escapeHTML(message) || "") + "</p>" ,
                buttons: [
                {text: _t('Ok'), close: true}]}).open();
        } else {
            // removed if exist error message
            this.$('#payment_error').remove();
            var messageResult = '<div class="alert alert-danger mb4" id="payment_error">';
            if (title != '') {
                messageResult = messageResult + '<b>' + _.str.escapeHTML(title) + ':</b></br>';
            }
            messageResult = messageResult + _.str.escapeHTML(message) + '</div>';
            $acquirerForm.append(messageResult);
        }
    },
    hideError: function() {
        this.$('#payment_error').remove();
    },
    /**
     * @private
     * @param {DOMElement} element
     */
    getAcquirerIdFromRadio: function (element) {
        return $(element).data('acquirer-id');
    },
    /**
     * @private
     * @param {jQuery} $form
     */
    getFormData: function ($form) {
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function (n, i) {
            indexed_array[n.name] = n.value;
        });
        return indexed_array;
    },
    /**
     * @private
     * @param {DOMElement} element
     */
    isFormPaymentRadio: function (element) {
        return $(element).data('form-payment') === 'True';
    },
    /**
     * @private
     * @param {DOMElement} element
     */
    isNewPaymentRadio: function (element) {
        return $(element).data('s2s-payment') === 'True';
    },
    /**
     * @private
     */
    updateNewPaymentDisplayStatus: function () {
        var checked_radio = this.$('input[type="radio"]:checked');
        // we hide all the acquirers form
        this.$('[id*="o_payment_add_token_acq_"]').addClass('d-none');
        this.$('[id*="o_payment_form_acq_"]').addClass('d-none');
        if (checked_radio.length !== 1) {
            return;
        }
        checked_radio = checked_radio[0];
        var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);

        // if we clicked on an add new payment radio, display its form
        if (this.isNewPaymentRadio(checked_radio)) {
            this.$('#o_payment_add_token_acq_' + acquirer_id).removeClass('d-none');
        }
        else if (this.isFormPaymentRadio(checked_radio)) {
            this.$('#o_payment_form_acq_' + acquirer_id).removeClass('d-none');
        }
    },

    disableButton: function (button) {
        $(button).attr('disabled', true);
        $(button).children('.fa-lock').removeClass('fa-lock');
        $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
    },

    enableButton: function (button) {
        $(button).attr('disabled', false);
        $(button).children('.fa').addClass('fa-lock');
        $(button).find('span.o_loader').remove();
    },
    _parseError: function(e) {
        if (e.message.data.arguments[1]) {
            return e.message.data.arguments[0] + e.message.data.arguments[1];
        }
        return e.message.data.arguments[0];
    },

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
//                setTimeout(function() {$empty_sol_del_error.hide()},12000);
                return false;
            }
        });
        return count;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    payEvent: function (ev) {
        ev.preventDefault();

        var form = this.el;
        var checked_radio = this.$('input[type="radio"]:checked');
        var self = this;
        var carrier_id = self.options.carrier;
        if(carrier_id.length === 0) {
            var result = this._checkSolDelivery();
            if (result == 0) {
                return false;
            }
        }

        if (ev.type === 'submit') {
            var button = $(ev.target).find('*[type="submit"]')[0]
        } else {
            var button = ev.target;
        }

        // first we check that the user has selected a payment method
        if (checked_radio.length === 1) {
            checked_radio = checked_radio[0];
            var form = document.getElementById("payment_form_next");
            form.submit();
            // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
        }
        else {
            this.displayError(
                _t('No payment method selected'),
                _t('Please select a payment method.')
            );
            this.enableButton(button);
        }
    },
    /**
     * Called when clicking on the button to add a new payment method.
     *
     * @private
     * @param {Event} ev
     */
    addPmEvent: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        var checked_radio = this.$('input[type="radio"]:checked');
        var self = this;
        if (ev.type === 'submit') {
            var button = $(ev.target).find('*[type="submit"]')[0]
        } else {
            var button = ev.target;
        }

        // we check if the user has selected a 'add a new payment' option
        if (checked_radio.length === 1 && this.isNewPaymentRadio(checked_radio[0])) {
            // we retrieve which acquirer is used
            checked_radio = checked_radio[0];
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            var acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
            // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
            var inputs_form = $('input', acquirer_form);
            var form_data = this.getFormData(inputs_form);
            var ds = $('input[name="data_set"]', acquirer_form)[0];
            var wrong_input = false;

            inputs_form.toArray().forEach(function (element) {
                //skip the check of non visible inputs
                if ($(element).attr('type') == 'hidden') {
                    return true;
                }
                $(element).closest('div.form-group').removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
                $(element).siblings( ".o_invalid_field" ).remove();
                //force check of forms validity (useful for Firefox that refill forms automatically on f5)
                $(element).trigger("focusout");
                if (element.dataset.isRequired && element.value.length === 0) {
                        $(element).closest('div.form-group').addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                        var message = '<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>';
                        $(element).closest('div.form-group').append(message);
                        wrong_input = true;
                }
                else if ($(element).closest('div.form-group').hasClass('o_has_error')) {
                    wrong_input = true;
                    var message = '<div style="color: red" class="o_invalid_field" aria-invalid="true">' + _.str.escapeHTML("The value is invalid.") + '</div>';
                    $(element).closest('div.form-group').append(message);
                }
            });

            if (wrong_input) {
                return;
            }
            // We add a 'processing' icon into the 'add a new payment' button
            $(button).attr('disabled', true);
            $(button).children('.fa-plus-circle').removeClass('fa-plus-circle');
            $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');

            // do the call to the route stored in the 'data_set' input of the acquirer form, the data must be called 'create-route'
            this._rpc({
                route: ds.dataset.createRoute,
                params: form_data,
            }).then(function (data) {
                // if the server has returned true
                if (data.result) {
                    // and it need a 3DS authentication
                    if (data['3d_secure'] !== false) {
                        // then we display the 3DS page to the user
                        $("body").html(data['3d_secure']);
                    }
                    // if it doesn't require 3DS
                    else {
                        // we just go to the return_url or reload the page
                        if (form_data.return_url) {
                            window.location = form_data.return_url;
                        }
                        else {
                            window.location.reload();
                        }
                    }
                }
                // if the server has returned false, we display an error
                else {
                    if (data.error) {
                        self.displayError(
                            '',
                            data.error);
                    } else { // if the server doesn't provide an error message
                        self.displayError(
                            _t('Server Error'),
                            _t('e.g. Your credit card details are wrong. Please verify.'));
                    }
                }
                // here we remove the 'processing' icon from the 'add a new payment' button
                $(button).attr('disabled', false);
                $(button).children('.fa').addClass('fa-plus-circle');
                $(button).find('span.o_loader').remove();
            }).guardedCatch(function (error) {
                error.event.preventDefault();
                // if the rpc fails, pretty obvious
                $(button).attr('disabled', false);
                $(button).children('.fa').addClass('fa-plus-circle');
                $(button).find('span.o_loader').remove();

                self.displayError(
                    _t('Server error'),
                    _t("We are not able to add your payment method at the moment.</p>") +
                        self._parseError(error)
                );
            });
        }
        else {
            this.displayError(
                _t('No payment method selected'),
                _t('Please select the option to add a new payment method.')
            );
        }
    },
    /**
     * Called when submitting the form (e.g. through the Return key).
     * We need to check whether we are paying or adding a new pm and dispatch
     * to the correct method.
     *
     * @private
     * @param {Event} ev
     */
    onSubmit: function(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        var button = $(ev.target).find('*[type="submit"]')[0]
        if (button.id === 'o_payment_form_pay') {
            return this.payEvent(ev);
        } else if (button.id === 'o_payment_form_add_pm') {
            return this.addPmEvent(ev);
        }
        return;
    },
    /**
     * Called when clicking on a button to delete a payment method.
     *
     * @private
     * @param {Event} ev
     */
    deletePmEvent: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        var self = this;
        var pm_id = parseInt(ev.target.value);

        var tokenDelete = function () {
            self._rpc({
                model: 'payment.token',
                method: 'unlink',
                args: [pm_id],
            }).then(function (result) {
                if (result === true) {
                    ev.target.closest('div').remove();
                }
            }, function () {
                self.displayError(
                    _t('Server Error'),
                    _t("We are not able to delete your payment method at the moment.")
                );
            });
        };

        this._rpc({
            model: 'payment.token',
            method: 'get_linked_records',
            args: [pm_id],
        }).then(function (result) {
            if (result[pm_id].length > 0) {
                // if there's records linked to this payment method
                var content = '';
                result[pm_id].forEach(function (sub) {
                    content += '<p><a href="' + sub.url + '" title="' + sub.description + '">' + sub.name + '</a><p/>';
                });

                content = $('<div>').html(_t('<p>This card is currently linked to the following records:<p/>') + content);
                // Then we display the list of the records and ask the user if he really want to remove the payment method.
                new Dialog(self, {
                    title: _t('Warning!'),
                    size: 'medium',
                    $content: content,
                    buttons: [
                    {text: _t('Confirm Deletion'), classes: 'btn-primary', close: true, click: tokenDelete},
                    {text: _t('Cancel'), close: true}]
                }).open();
            }
            else {
                // if there's no records linked to this payment method, then we delete it
                tokenDelete();
            }
        }, function (err, event) {
            self.displayError(
                _t('Server Error'),
                _t("We are not able to delete your payment method at the moment.") + err.data.message
            );
        });
    },
    /**
     * Called when clicking on 'and more' to show more payment icon.
     *
     * @private
     * @param {Event} ev
     */
    onClickMorePaymentIcon: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $listItems = $(ev.currentTarget).parents('ul').children('li');
        var $moreItem = $(ev.currentTarget).parents('li');
        $listItems.removeClass('d-none');
        $moreItem.addClass('d-none');
    },
    /**
     * Called when clicking on a radio button.
     *
     * @private
     * @param {Event} ev
     */
    radioClickEvent: function (ev) {
        // radio button checked when we click on entire zone(body) of the payment acquirer
        $(ev.currentTarget).find('input[type="radio"]').prop("checked", true);
        this.updateNewPaymentDisplayStatus();
    },
});
return publicWidget.registry.PaymentForm;
});


