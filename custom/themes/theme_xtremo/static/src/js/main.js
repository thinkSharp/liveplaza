odoo.define("theme_xtremo.main.js", function (require) {
  "use strict";

  var self = require('xtremo.core');
  var execute = [];

  function copy_menu_to_mobile() {
    var appended = self.getQuery("#xtremo_mobile_menu .xt-cart");
    var _user = self.getQuery('#xtremo_user_header >.dropdown-menu').cloneNode(true);
    var _menus = self.getQuery(".o_affix_enabled #top_menu").cloneNode(true);
    _user.classList.remove("dropdown-menu","dropdown-menu-right");
    _user.classList.add("user_menu_bar","hide");
    _menus.classList.add("user_menu_bar_main");
    let name = _user.querySelector('a.user-name');
    let contact = _menus.querySelector('li.contact_no');
    if (name){
      _user.insertBefore(name, _user.childNodes[0]);
    }
    appended.appendChild(_user);
    appended.appendChild(_menus);
  };

  function makeSimpleMegaMenu() {
    $(".xtremo_mega_simple_dropdown_menu").closest('li').removeClass("position-static");
  }

  function set_user_dropdown() {
    let drop_down = self.getQuery(".dropdown-menu.js_usermenu");
    self.getId("xtremo_user_header").appendChild(drop_down);
  };

  function user_menu(event) {
    self.getId('xtremo_mobile_menu').classList.add("active");
    self.getQuery("header.o_affix_enabled").style.zIndex = "50000";
  };

  function user_menu_close(event) {
    event.stopPropagation();
    if (event.currentTarget.id == "xtremo_mobile_menu"){
      this.classList.remove("active");
      this.style.zIndex = "1035";
    }
  };

  function toggle_user_menu() {
    $('.toggle-user-menu').removeClass("active");
    var user = self.getQuery('.user_menu_bar') ;
    var menus = self.getQuery(".user_menu_bar_main");
    if (this.getAttribute('name') == 'menu'){
      user.classList.add('hide');
      menus.classList.remove('hide');
    }
    if (this.getAttribute('name') == 'user'){
      menus.classList.add('hide');
      user.classList.remove('hide');
    }
    this.classList.add('active');
  };


  function resizeScript (ev){
    if (!self.isMobile()) {
      self.getQuery("header.o_affix_enabled").style.zIndex = "1037";
    }
  };

  function append_clasess_load(){
    var doc = self.getQuery(".oe_website_sale.py-2");
    if (doc){
      var href = window.location.pathname;
      if(href.includes("/shop/cart")){
        doc.classList.add("cart");
      }
      if(href.includes("/shop/address")){
        doc.classList.add("address");
      }
      if(href.includes("/shop/checkout")){
        doc.classList.add("checkout");
      }
      if(href.includes("/shop/payment")){
        doc.classList.add("payment");
      }
    }
  };


  execute.push(set_user_dropdown);
  execute.push(copy_menu_to_mobile);
  execute.push(append_clasess_load);
  execute.push(makeSimpleMegaMenu);

  $(document).ready(function() {
    self.get_resolve(execute);
    try {
      // events..
      self.getQuery('#xt-mobile-menu button').addEventListener("click",user_menu);
      self.getId('xtremo_mobile_menu').addEventListener("click",user_menu_close);
      self.getQuery('#xtremo_mobile_menu .xt-cart').addEventListener("click",user_menu_close);
      self._click('toggle-user-menu',toggle_user_menu);
      window.addEventListener("resize", resizeScript);
    } catch (e) {
      console.error("xtremo main...");
    }

  });

  $(document).ready(function(){
    if(window.location.pathname.includes("/shop/confirmation")){
      $('.container.oe_website_sale.py-2 .row').addClass("confirmation");
    }
    if(window.location.pathname.includes("/my/account")){
      $('.container.mb64').addClass("my_account_details");
    }
  });

})

odoo.define('xtremo.mega.menu', function (require) {
  var publicWidget = require('web.public.widget');

  publicWidget.registry.mobileMegaMenu = publicWidget.Widget.extend({

    selector: ".xt-cart",

    events: {
      "click .o_mega_menu_toggle": "_showMenu",
      "click .header": '_hideMenu'
    },

    _showMenu: function (ev) {
      $(".o_mega_menu").removeClass("show");
      $(".o_mega_menu").find(".header").remove();
      var $ul = $(ev.currentTarget).closest("li").find(".o_mega_menu");
      var html = `<div class='header d-flex'><span class="fa fa-angle-left" /> <span>${$(ev.currentTarget).text()}</span></div>`
      $ul.find("section").first().before(html);

      if ($(ev.currentTarget).closest("li").hasClass("position-static")) {
        this.top = $(".xt-cart").scrollTop();
        $(".xt-cart").scrollTop(0)
      }
      $ul.addClass("show");
    },

    _hideMenu: function (ev) {
      var $ul = $(ev.currentTarget).closest("li").find(".o_mega_menu");
      if ($(ev.currentTarget).closest("li").hasClass("position-static")) {
        $(".xt-cart").scrollTop(this.top);
      }
      $ul.removeClass("show");
      $(ev.currentTarget).remove();
    }

  });
});

odoo.define('xtremo.beauty.carousal', function (require) {
  "use strict";
  var publicWidget = require('web.public.widget');
  var xxx = new publicWidget.RootWidgetRegistry();
  var publicRootData = require('web.public.root');

  var xtremoBeautyCarousal = publicWidget.RootWidget.extend({
    // selector: ".xtremo-website-beauty-1",
    events: _.extend({}, publicWidget.RootWidget.prototype.events || {}, {
      'click .left-side': "_slideLeft",
      'click .right-side': "_slideRight"
    }),

    _getRegistry: function () {
        return xxx;
    },


    start: function () {
      var self = this;
      this.target = this.el;
      this.$target = this.$el;
      this.$carousalConatiner = this.target.querySelector(".xtremo-container");
      this.$items = this.$carousalConatiner.querySelector(".item");
      this.$leftSlider = this.target.querySelector(".left-side");
      this.$rightSlider = this.target.querySelector(".right-side");
      this.sliderParameter = this.$items.offsetWidth;
      this.maxWidth = this.$carousalConatiner.scrollWidth;
      this.visibleConatianer = this.$carousalConatiner.offsetWidth;
      this.factor = Math.ceil(this.sliderParameter / 30);
      this.active = true;

      if (this.$items.length > 3) {
        this.$leftSlider.style.display = "none";
        this.$rightSlider.style.display = "none";
      } else if (window.screen.width < 768){
        this.$leftSlider.style.display = "none";
        this.$rightSlider.style.display = "none";
      } else {
        this.$leftSlider.style.display = "flex";
        this.$rightSlider.style.display = "flex";
      }
      return this._super.apply(this, arguments);
    },

    _slideLeft: function (ev) {
      if (this.active){
        this.animation(false);
      }
    },

    _slideRight: function (ev) {
      if (this.active){
        this.animation(true);
      }
    },

    animation: function (type) {
      var self = this;
      var nPosition = 0;
      var hasDone;
      var left = 0;
      var right = 0;
      self.active = false;
      window.cancelAnimationFrame(hasDone);
      var doAnimation = function () {
        if (nPosition >= self.sliderParameter) {
          if (type) {
            self.$carousalConatiner.appendChild(self.$carousalConatiner.querySelector(".item"));
            self.$carousalConatiner.scrollLeft = self.$carousalConatiner.scrollLeft - self.sliderParameter;
          } else {
            var last_item = self.$carousalConatiner.querySelectorAll(".item");
            self.$carousalConatiner.insertBefore(last_item[last_item.length -1], self.$carousalConatiner.querySelector(".item"));
            self.$carousalConatiner.scrollLeft = self.sliderParameter;
          }
          self.active = true;
          window.cancelAnimationFrame(hasDone);
          return;
        } else {

            if (nPosition + self.factor > self.sliderParameter){
              right += self.sliderParameter - nPosition;
              left -= self.sliderParameter - nPosition;
            } else {
              right = self.$carousalConatiner.scrollLeft + self.factor;
              left = self.$carousalConatiner.scrollLeft - self.factor;
            }

          type ? self.$carousalConatiner.scrollLeft = right : self.$carousalConatiner.scrollLeft = left;
          nPosition += self.factor;
          hasDone = window.requestAnimationFrame(doAnimation);
        }
      }
      doAnimation();
    },


  })

  publicRootData.publicRootRegistry.add(xtremoBeautyCarousal, '.xtremo-website-beauty-1');

  return {
      xxx: xxx
    };

});
