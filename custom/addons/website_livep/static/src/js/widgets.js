odoo.define('website_livep', function (require) {
  'use strict';

  var publicWidget = require('web.public.widget');
  var ajax = require('web.ajax');
  var utils = require('web.utils');
  var session = require('web.session');

  publicWidget.registry.websiteLivepSearch = publicWidget.Widget.extend({
    selector: '.js-search-box',
    events: {
      'click .js-search-submit': '_onSearchSubmit',
    },

    /**
     * @Override
     */
    start: function() {
      var def = this._super.apply(this, arguments)
      return def;
    },

    // --------
    // Handlers
    // --------

    /**
     * @private
     */
    _onSearchSubmit: function(event) {
      event.preventDefault()
      var text = this.$('.js-search-text').val()
      if(text.length > 0) {
        var path = this.$('.js-search-path').val()
        var query = `search=${text}`
        window.location.href = `${path}?${query}`
      }
    },
  })


  publicWidget.registry.websiteLivepSlidein = publicWidget.Widget.extend({
    selector: '.js-slidein-control',
    events: {
      'click': '_onSlideinAction',
    },

    /**
     * @override
     */
    start: function () {
      var def = this._super.apply(this, arguments)
      return def;
    },


    // ---------
    // Handlers
    // ---------

    /**
     * @private
     */
    _onSlideinAction: function(event) {
      var $target = $(event.currentTarget)
      var $openTarget = $($target.data('slidein-open'))
      var $closeTarget = $($target.data('slidein-close'))
      $openTarget.addClass('active')
      $closeTarget.removeClass('active')
    },
  })


  publicWidget.registry.websiteLivepCart = publicWidget.Widget.extend({
    selector: '.js-cart',
    events: {
      'click .js-cart-remove': '_onRemove',
    },

    /**
     * @override
     */
    start: function() {
      var ref = this;
      var def = this._super.apply(this, arguments)
      ref._updateCart()
      return def
    },

    _html: function(data) {
      this.$el.html(data)
    },

    /**
     * @private
     */
    _updateCart: function() {
      var ref = this;
      ref._html('Updating cart...')
      $.get('/website_livep/cart/')
        .then(function (data) {
          var $cart = $(data)
          ref._html($cart)
        })
        .catch(function () {
          ref._html('Error while loading shoping cart.')
        })
    },

    /**
     * @private
     */
    _onRemove: function(event) {
      var ref = this;
      var $target = $(event.currentTarget)
      var line_id = $target.data('cart-lid')
      var product_id = $target.data('cart-pid')
      ajax.jsonRpc("/shop/cart/update_json", "call", {
        line_id,
        product_id,
        'set_qty': 0,
      }).then(function (){
        ref._updateCart()
      }).catch(function () {
        ref._html('Update error.')
      })
    },
  })

  publicWidget.registry.websiteLivepCompare = publicWidget.Widget.extend({
    selector: '.js-compare-list',

    /**
     * @override
     */
    start: function() {
      var ref = this
      var def = this._super.apply(this, arguments)
      ref._update()
      return def
    },


    /**
     * @private
     */
    _html: function(data) {
      this.$el.html(data)
    },

    /**
     * @private
     */
    _update: function() {
      var ref = this
      ref._html('Updating compare list...')
      $.get('/website_livep/compare_list/', {
        'product_ids': ref._get_compare_list().join(',')
      }).then(function (data) {
          var $cart = $(data)
          ref._html($cart)
        })
        .catch(function () {
          ref._html('Error while loading compare list.')
        })
    },

    /**
     * @private
     */
    _get_compare_list: function() {
      var user_id = session.user_id
      var cookie_name = user_id ? user_id + '_compare' : 'guest_compare'
      var cookie_string = utils.get_cookie(cookie_name)
      var compare_list = cookie_string ? JSON.parse(cookie_string) : []
      return compare_list
    },
  })
})