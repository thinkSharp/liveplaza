/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('xtremo.comparison', function (require) {
'use strict';

  var core = require('web.core');
  var publicWidget = require('web.public.widget');
  var _t = core._t;
  var utils = require('web.utils');
  var ajax = require('web.ajax');
  var website_sale_utils = require('website_sale.utils');
  var old_compare = require('website_sale_comparison.comparison');

  publicWidget.registry.ProductComparison = publicWidget.registry.ProductComparison.extend({
    events: {}
  });

  publicWidget.registry.xtremoComparision = publicWidget.Widget.extend({
    selector: '.o_affix_enabled #compare a',
    xmlDependencies: ['/theme_xtremo/static/src/xml/xtremo_dynamic_modal.xml'],
    read_events: {
      'click': '_openModal'
    },

    start: function(){
      var ref = this;
      ref.$target.attr({
        "data-toggle": "tooltip",
        "data-placement": "bottom",
        "title": _t("Show Comparision")
      });
      var res = {
        "t_id": "xtremo_comparision_modal",
        "t_header": _t("My Compare List"),
        't_button': `<a style="width: 100%;" role="button" class="btn btn-primary" href="/shop/cart">${ _t("Compare") }</a>`
      };
      var html = $(core.qweb.render('theme_xtremo.dynamic_modal', res));
      $('main').append(html);
      var computeCompare = ref._callCompare;
      var product_ids = JSON.parse(utils.get_cookie('comparelist_product_ids') || '[]');
      var proceed = ref._validRequest(product_ids.length, 0, false);
       $("#xtremo_comparision_modal").find('.modal-footer a').hide();
      if (proceed){
        computeCompare(ref, product_ids, product_ids);
      }
      $('.o_add_compare, .js_main_product .o_add_compare_dyn').off('click').on('click', function(ev){
        ev.preventDefault();
        var product_id = parseInt($(this).attr('data-product-product-id'));
        var cookie = JSON.parse(utils.get_cookie('comparelist_product_ids') || '[]');
        var presents = cookie.indexOf(product_id) > -1 ;
        var proceed = ref._validRequest(1, cookie.length, presents);
        if (((! presents) || (cookie.length <= 0)) && proceed){
          computeCompare(ref, [product_id], cookie);
          setTimeout(function(){
            website_sale_utils.animateClone(
             $('.o_affix_enabled #compare'),
             $(ev.currentTarget).closest('form'), 0 , 0
            );
          },100);
        }else{
          $("#xtremo_comparision_modal").modal('show');
          $('body').removeClass('modal-open');
        }
      })
    },

    _callCompare: function (self, product_ids, cookie) {
      ajax.jsonRpc('/shop/get_product_data', 'call',
          {
              "product_ids": product_ids,
              "cookies": cookie
          }
        ).then(function (data) {
         var $el = $("#xtremo_comparision_modal .modal-body");
         cookie = data.cookies
         utils.set_cookie('comparelist_product_ids', cookie, false);
         delete data.cookies;
         var html = "";
         for (let [key, value] of Object.entries(data)) {
           html += value.render;
         }
         $el.find('.alert').remove();
         $el.append(html);
         self._setCompareButtonUrl(JSON.parse(cookie));
         var fun = self._deleteItem()
         $("#xtremo_comparision_modal .o_remove").on("click", fun);
      });
    },

    _openModal: function () {
      $("#xtremo_comparision_modal").modal('show');
      // $('body').removeClass('modal-open');
    },

    _deleteItem: function (){
      var ref = this;
      return function(ev){
        ev.preventDefault();
        ev.stopPropagation();
        var cookie = JSON.parse(utils.get_cookie('comparelist_product_ids') || '[]');
        var product_id = parseInt($(this).attr('data-product_product_id'));
        if (cookie.indexOf(product_id) >= 0){
          cookie.splice(cookie.indexOf(product_id), 1);
          $(this).parents('.o_product_row').remove();
        }
        utils.set_cookie("comparelist_product_ids", JSON.stringify(cookie), false);
        $("#xtremo_comparision_modal .modal-body").find('.alert').remove();
        ref._setCompareButtonUrl(cookie);
        ref._validRequest(cookie.length, 0, false);
      }
    },

    _alertMessage: function(message){
      return `<div style="text-align: center;" class="alert alert-primary mt-2">
                <span><i class="fa fa-exclamation-triangle mr-2"></i>   ${message}</span>
              </div>`;
    },

    _validRequest: function (length_1, length_2, presents) {
      var message = false;
      if (presents){
        message = _t("Product already exists in your Compare List");
      }
      else if (length_1 == 0){
        message = _t("No Products found in your Compare List");
      }
      else if (length_2 >= 4){
        message = _t("You can compare max 4 products");
      }
      if ( message != false){
        $("#xtremo_comparision_modal .modal-body").find('.alert').remove();
        $("#xtremo_comparision_modal .modal-body").append(this._alertMessage(message));
        return false;
      }
      return true;
    },

    _setCompareButtonUrl: function (cookie){
      var $el = $("#xtremo_comparision_modal").find('.modal-footer a');
      var sup = $("#compare sup")
        sup.text(cookie.length)
        .addClass("o_red_highlight");
      setTimeout(function(){sup.removeClass("o_red_highlight");},1000);
      if (cookie.length > 1){
        var url = cookie.toString();
        var href = `/shop/compare/?products=${ url }`;
        $el.attr("href",href).show();
      } else {
        $el.hide();
      }
    }

  });
});
