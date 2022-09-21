/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('theme.xtremo.lazy_loading', function (require) {
    "use strict";
    var core = require('web.core');
    var sAnimations = require('website.content.snippets.animation');

    sAnimations.registry.ProductLazyLoad = sAnimations.Class.extend({
      selector: "div#wk_loader",
      read_events: {
        'click button': '_loadProducts'
      },
      start: function() {
        var $ref = this;
        $ref.page = parseInt(1);
      },

      _loadProducts: function() {
        var $ref = this;
        $ref._loader("block", "none");
              var $el = $ref.$target;
              $ref.page += 1;
              var href = window.location.href;
              var replace="";
//              if(!href.includes('/shop')){
//                href+='shop';
//              }
              if (href.indexOf("?") > -1 && href.indexOf("?") > href.indexOf("#") && href.indexOf("#") > -1){
                replace = href.substring(href.indexOf("#"),href.indexOf("?"));
              }else if(href.indexOf("#") > -1){
                replace = href.substring(href.indexOf("#"), href.length);
              }
              href = href.replace(replace, "").split("?");
              if ( href.length > 1 ) {
                href = `${ href[0] }/page/${ $ref.page }?${ href[ href.length - 1 ] }&view=list`;
              } else {
                href = `${ href[0] }/page/${ $ref.page }?view=list`;
              }
              if(href.includes('/sellers/list')){
                $ref._callProducts(href, $ref, "seller");
              }
              else if (href.includes('/livestreams')) {
                $ref._callProducts(href, $ref, "livestream");
              }
              else{
                $ref._callProducts(href, $ref, "product");
              }

      },

      _callProducts: function (href, $ref, type) {
        $.get( href,{"test":href}, function (data){
          if (data == 'none') {
            var html = `<i class="fa fa-exclamation-triangle"></i><br/><strong>You've reached the end.</strong>`;
            $ref.$target.html(html);
          } else {
            if(type == "seller"){
                $("#sellers_grid tbody tr:last").after(data);
            }
            else if(type == "livestream"){
                $("#livestreams_grid tbody tr:last").after(data);
            }
            else{
                $("#products_grid tbody tr:last").after(data);
            }
            $ref._loader("none", "block");
          }
          $('.xt_product_count-to').text($('#products_grid .oe_product_cart').length);
        })
      },

      _loader: function (_x1, _x2){
        this.$target.find("span").css('display', _x1);
        this.$target.find("p").css('display', _x1);
        this.$target.find("button").css('display', _x2);
      }

    });

});
