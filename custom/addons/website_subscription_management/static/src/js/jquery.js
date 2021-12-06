/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('website_subscription_management.selection', function(require) {
    "use strict";

    var core=require('web.core');
    var ajax=require('web.ajax');
    var _t=core._t;

    $(document).ready(function () {
        $(document).on('click','#renew,.renew_table',function(){
            var rec_id = $('.rec_id').text();
            ajax.jsonRpc('/website/json/controller','call',{
                'renew':rec_id,
            })
            .then(function(data){
                location.reload();
            })
            
        });

        $('.js_main_product input').on('change',function(){
            var product_id = $(".product_id").attr('value');
            ajax.jsonRpc('/check/product_variant/subscription','call',{
                'product_id':product_id,            
            })
            .then(function(data){
                if(data==false){
                    // $('.css_quantity.input-group.oe_website_spinner').removeClass('hidden');
                    $('#subPlan_info').hide();

                }
                else{
                    $('#subPlan_info').show();
                    // $('.css_quantity.input-group.oe_website_spinner').addClass('hidden');
                    var dehighligh_element=$('.add_color').removeClass('add_color');
                    var highlight_element=Boolean($('[data-id='+product_id+']').addClass('add_color'));  
                }
            })
        });

     });
});
