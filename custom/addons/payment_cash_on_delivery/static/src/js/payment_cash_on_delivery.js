/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('website_lazy_loading.wk_lazy', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    $(document).ready(function() {

        $('[data-toggle="popover"]').popover();
        var payment_cod = $("#payment_cod");
        var payments = payment_cod.find("input[name='pm_id']");
        if (payment_cod.length>0) {
            if(payment_cod.hasClass('disabled')){
                payments.prop('disabled',true);
                payment_cod.find(">div.text-muted").addClass("d-none");
                payment_cod.on('click',function(ev){ev.preventDefault();ev.stopPropagation()});
            }
        }
    });
})
