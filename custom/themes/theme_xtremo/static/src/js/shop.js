odoo.define('theme_xtremo.shop_page_filter_js', function (require) {
  'use strict';

  var core = require('web.core');
  var _t = core._t;

  $(document).ready(function(){

    var html = `<h6 class="filter">All Categories</h6>`;
    $('#products_grid_before #wsale_products_categories_collapse').prepend(html);
    html = `<h6 class="filter">Filters</h6>`;
    $('#products_grid_before #wsale_products_attributes_collapse').prepend(html);
    $('#products_grid_before #select_price_range >h6').addClass("filter").css("margin-bottom","50px");

    // Filter
    $(".attribute_category_filter").click(function(){
      $("#products_grid_before").toggleClass('attribute_category_filter_slider');
      var html = "<div class='background-modal' />";
      $('.background-modal').remove();
      $('body').append(html);
      $('.background-modal').on('click', function (ev) {
        $(".attribute_category_filter_close").trigger('click');
      });
    });
    $(".attribute_category_filter_close").click(function(){
      $("#products_grid_before").removeClass('attribute_category_filter_slider');
      $('.background-modal').remove();
    });
    
  });
});
