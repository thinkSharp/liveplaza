odoo.define('xtremo.shop.advance.search', function (require) {
  "use strict";
  var sAnimations = require('website.content.snippets.animation');
  var self = require('xtremo.core');
  var publicWidget = require('web.public.widget');
  var wSaleUtils = require('website_sale.utils');

  $(document).on('click', "main", function(ev) {
    $("#xtremo_top_menu .xtremo_search").removeClass("open");
  });

  publicWidget.registry.ProductWishlist = publicWidget.registry.ProductWishlist.extend({
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

            if (productId && !_.contains(self.wishlistProductIDs, productId)) {
                return self._rpc({
                    route: '/shop/wishlist/add',
                    params: {
                        product_id: productId,
                    },
                }).then(function () {
                    self.wishlistProductIDs.push(productId);
                    self._updateWishlistView();
                    if (window.screen.width > 767) {
                      wSaleUtils.animateClone($('#xtremo_user_header'), $el.closest('form'), 25, 40);
                    }
                }).guardedCatch(function () {
                    $el.prop("disabled", false).removeClass('disabled');
                });
            }
        }).guardedCatch(function () {
            $el.prop("disabled", false).removeClass('disabled');
        });
    },
  });

  publicWidget.registry.autohideMenu = publicWidget.registry.autohideMenu.extend({
    start: function () {
      var ref = this;
      this._super.apply(this, arguments).then(function (response) {
        ref.set_header();
        return response;
      })
    },

    set_header: function (){
      var _margin = 0;
      this.$target.parents("header").find(".navbar").each(function() {
        _margin += this.offsetHeight;
      });
      document.querySelector("main").style.marginTop = `${_margin}px`;
    }
  })

  publicWidget.registry.shopAdvanceSearch = publicWidget.Widget.extend({
    selector: "#xtremo_top_menu .xtremo_search",
    events: {
      "click .input-group-append button": '_search',
      'click .input-group-prepend li': '_setCategory',
      'keypress input[type="text"]': '_pressEnterKey',
      'mouseenter .input-group-append button': '_mouseenter'
    },

    start: function () {
      var textBox = $("#xtremo_mobile_menu input[type='text']");
      var searchMobile = $("#xtremo_mobile_menu .col-sm-12 .fa-search");
      textBox.on('keypress', this._getSearch);
      searchMobile.on('click', this._getSearch);
    },

    _search: function () {
      var $target = this.$target;
      var searchString = $target.find("input[type='text']").val();
      var category = $target.find('button .text').attr("data");
      if (searchString.length > 0){
        let url = category != "0" ? `${category}?search=${searchString}` : `/shop?search=${searchString}`;
        window.location.href = url;
      }
    },

    _setCategory: function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      var categoryUrl = ev.currentTarget.querySelector("a").getAttribute("href");
      var categoryString = ev.currentTarget.querySelector("a").textContent;
      var $el = this.$target.find('.input-group-prepend .text');
      categoryString = categoryString.length > 15 ? categoryString.substring(0,12).concat("...") : categoryString;
      $el.text(categoryString).attr("data", categoryUrl);
    },

    _pressEnterKey: function (ev) {
      if (ev.keyCode === 13) {
        this._search();
      }
    },

    _getSearch: function (ev) {
      var bool = ev.currentTarget.classList.contains("fa-search");
      var searchString = "";
      if (bool) {
        var searchString = $("#xtremo_mobile_menu input[type='text']").val();
      } else if (ev.keyCode === 13) {
        var searchString = ev.currentTarget.value;
      }
      if (searchString.length > 0){
        window.location.href = `/shop?search=${searchString}`;
      }
    },

    _mouseenter: function(ev) {
      this.$target.addClass('open');
    }

  });

  publicWidget.registry.WebsiteSaleLayout = publicWidget.registry.WebsiteSaleLayout.extend({
    start: function () {
      this._super();
      if ( this.$target.find('.o_wsale_apply_layout').length > 0 ) {
        $(window).resize(this.resize);
      }
    },

    _onApplyShopLayoutChange: function (ev) {
      var switchToList = $(ev.currentTarget).find('.o_wsale_apply_list input').is(':checked');
      var layout = switchToList ? 'list' : 'grid';

      if (window.screen.width < 768) {
        layout = "list";
        switchToList = true;
      }



      if (!this.editableMode) {
          this._rpc({
              route: '/shop/save_shop_layout_mode',
              params: {
                  'layout_mode': layout,
              },
          });
        }

        var $grid = this.$('#products_grid');
        $grid.find('*').css('transition', 'none');
        $grid.toggleClass('o_wsale_layout_list', switchToList);
        void $grid[0].offsetWidth;
        $grid.find('*').css('transition', '');
    },

    resize: function (ev) {
      $('.o_wsale_apply_layout').trigger('change');
    }

  })

  publicWidget.registry.affixMenu = publicWidget.registry.affixMenu.extend({
    start: function(){
      this._super.apply(this, arguments);
      this.lastScrollTop = 0;
      this.timer = false;
      var fun = this._mouseWheel();
      $(window).scroll(fun);
      this.destroy();
    },
    _onWindowUpdate: function () {},

    _mouseWheel: function(){
      var $ref = this;
      return function (e) {
        var st = window.pageYOffset || document.documentElement.scrollTop;
        var $el = $ref.$target.find(">.navbar");
        if (st > $ref.lastScrollTop){
            var bool = $ref._getPositionMouse();
            if (bool){
              $el.css("top", "0%");
            }else{
              $el.css("top", "100%");
            }
         } else {
            clearTimeout($ref.timer);
            $ref.timer = setTimeout(function () {
              $el.css("top", "100%");
            }, 100);
         }
         $ref.lastScrollTop = st <= 0 ? 0 : st;
      }
    },

    _getPositionMouse: function (){
      var wOffset = $(window).scrollTop();
      var hOffset = this.$target.scrollTop();
      var isMegaMenu = $(".o_mega_menu.show");
      if( (wOffset > (hOffset + 300)) && (isMegaMenu.length <= 0) ){
        return true;
      }
      return false;
    }

  });


});

odoo.define('xtremo.scroll.to.top', function (require) {
  "use strict";
  var publicWidget = require('web.public.widget');
  publicWidget.registry.scrollBottomToTop = publicWidget.Widget.extend({
    selector: "#xtremo_scroll_top",
    events: {
      'click span': '_scrollUp'
    },

    start: function (){
      var $self = this.$target;
      window.addEventListener("scroll", this.showScroller);
    },

    _scrollUp: function (){
      window.scrollTo(0, 0);
    },

    showScroller: function (){
      var $ele = $("#xtremo_scroll_top");
      if (window.scrollY > 320 && ! $ele.hasClass("show-scroll")){
        $ele.addClass('show-scroll');
      }else if(window.scrollY < 320 && $ele.hasClass("show-scroll")) {
        $ele.removeClass('show-scroll');
      }
    }

  });


});

odoo.define('xtremo.home.featues', function (require) {
  "use strict";
  var ajax = require('web.ajax');
  var publicWidget = require('web.public.widget');
  var xtremo_core = require('xtremo.core');

  publicWidget.registry.render_feature_prodcuts = publicWidget.Widget.extend({
    selector: ".xtremo_home_feature",

    start: function(){
      var $self = this.$target;
      var calls = $self.data("ref");
      ajax.jsonRpc("/xtremo/get-feature", 'call', {"ref": calls})
       .then(function (data) {
            $self.html(data);
            xtremo_core.owl_for_home($self);
       })
    }
  });
});

odoo.define('xtremo.website.beauty', function (require) {
  "use strict";
  var core = require('web.core');
  var ajax = require('web.ajax');
  var publicWidget = require('web.public.widget');
  var xtremo_core = require('xtremo.core');

  publicWidget.registry.xtremoBeautyAnimation = publicWidget.Widget.extend({
    selector: ".xtremo-website-beauty",
    read_events: {
      'mousemove .x-img img': '_imageMovement',
      'mouseout .x-img img': '_imageMovementOut',
      'click .x-img img': '_showMobileBeautyCarousel',
      'click .x-open-icon': '_showBeautyCarousel',
      'click .cancel': '_cancelCarousel',
    },

    start: function(){

      this.$target.mousewheel(this._mouseWheel);
      this.$target.find('.x-img').css("transform", "translate3D(0,0,0)");
    },

    _showMobileBeautyCarousel: function(e){
      if(window.screen.width < 768){
        this._showBeautyCarousel(e);
      }
    },

    _imageMovement: function(e){
      this.getAnimate(e);
    },

    _imageMovementOut: function(e){
      e.currentTarget.parentElement.style.transform = "translate3D(0,0,0)";
    },

    getAnimate: function(e){
      var left = e.offsetX;
      var top = e.offsetY;
      var width = e.currentTarget.offsetWidth/2;
      var height = e.currentTarget.offsetHeight/2;
      const move = 8;
      var postionL = ((left - width)*100)/width;
      var postionT = ((top - height)*100)/height;
      var x = (postionL*move)/100;
      var y = (postionT*move)/100;
      e.currentTarget.parentElement.style.transform = `translate3D(${x}px,${y}px,0)`;
    },

    _createBeautyCarousel: function(e){
      var html = `<div class="xtremo-beauty-modal open-modal"><div class="cancel"><span>X</span></div>
                    <div id="carouselControls" class="carousel slide" data-ride="carousel">
                      <div class="carousel-inner">`;
      var $self = this.$target;
      var imges = $self.find('img');
      var cSrc = e.currentTarget.parentElement.querySelector('img').getAttribute('src');
      imges.each(function(){
        var src = $(this).attr("src");
        var cl = (src == cSrc) && ! html.includes('active') ? 'active' : '';
        html += `<div class="carousel-item ${cl}"><div class="carousel-img"><div><img src="${src}" /></div></div></div>`;
      })
      html += `</div>
                  <a class="carousel-control-prev" href="#carouselControls" role="button" data-slide="prev">
                    <i class="fa fa-arrow-left"></i>
                  </a>
                  <a class="carousel-control-next" href="#carouselControls" role="button" data-slide="next">
                    <i class="fa fa-arrow-right"></i>
                  </a>
                </div>
              </div>`;
      $self.append(html);
    },

    _showBeautyCarousel: function(e){
      var item = this.$target.find('.xtremo-beauty-modal');
      if(item.length > 0){
        item.find('.carousel-item ').removeClass('active');
        var cSrc = e.currentTarget.parentElement.querySelector('img').getAttribute('src');
        item.find(`img[src="${cSrc}"]`).first().parents('.carousel-item').addClass('active');
        item.addClass('open-modal');
      }
      else{
        this._createBeautyCarousel(e);
      }

    },

    _cancelCarousel: function(){
      this.$target.find('.xtremo-beauty-modal').removeClass('open-modal');
    },

    _mouseWheel: function(e){
      var element = e.currentTarget;
      var scrollPosition = element.scrollLeft;
      var scrollWidth = element.scrollWidth-element.offsetWidth-1;
      var navAdmin = document.getElementById('oe_main_menu_navbar');
      var windowTop = document.querySelector('.o_affix_enabled').offsetHeight + document.querySelector('.o_affix_enabled >.navbar').offsetHeight;
      windowTop = navAdmin ? navAdmin.offsetHeight + windowTop : windowTop;
      if(e.deltaY < 0 && scrollWidth > scrollPosition){
        e.preventDefault();
        window.scrollTo(0, element.offsetTop-windowTop+30);

        animateScroll(element, element.scrollLeft, true);
      }
      else if(e.deltaY  > 0 && scrollPosition > 1){
        e.preventDefault();
        window.scrollTo(0, element.offsetTop-windowTop+30);
        animateScroll(element, element.scrollLeft, false);
      }

      function animateScroll(target, postion, type){
        var nPosition = postion;
        var animmy;
        window.cancelAnimationFrame(animmy);
        var animate = function(){
          if(nPosition >= postion+100 || nPosition <= postion-100){
            window.cancelAnimationFrame(animmy);
            return;
          }
          nPosition = type ? (nPosition += 5) : nPosition -= 5;
          target.scrollLeft = nPosition;
          animmy = window.requestAnimationFrame(animate);
        }
        animate();
      }

    },

  });
});



odoo.define('xtremo.set.contactus.page', function (require) {
  "use strict";
  var publicWidget = require('web.public.widget');

  publicWidget.registry.setConatactUsPage = publicWidget.Widget.extend({
    selector: ".xtremo_contact_us_form",
    start: function () {
      $("main").addClass("contact-us");
      $(".container.mt-2").addClass("xtremo-contact-form")
      var $el = this.$target.clone();
      $el.removeClass("active").show();
      this.$target.hide();
      $("#wrap .oe_structure").first().append($el);
    }
  })
});

odoo.define('xtremo.banner.with.category', function (require) {
  "use strict";
  var ajax = require('web.ajax');
  var publicWidget = require('web.public.widget');

  publicWidget.registry.xtremoBannerWithCategory = publicWidget.Widget.extend({
    selector: ".xtremo_banner_with_category",
    start: function(){
      var $self = this.$target;
      ajax.jsonRpc("/xtremo/get-category-feature", 'call', {})
       .then(function (data) {
          $self.find('.remove-ul').html(data);
      })
    }
  });
});
