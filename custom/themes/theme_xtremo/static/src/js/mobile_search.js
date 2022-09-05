odoo.define('livep.search.mobile', function(require) {
  "use strict";
  
  var publicWidget = require('web.public.widget')

  publicWidget.registry.LivvepMobileSearch = publicWidget.Widget.extend({
    selector: '.js-mobile-search',
    events: {
      "click .dropdown-item": "_setCategory",
    },

    /**
     * @override
     */

    start: function () {
      var ref = this;
      ref.$dropdownItems = this.$el.find('.dropdown-item')
      ref.$form = this.$el.find('form')
      ref.$indicator = this.$el.find('.category-indicator')

      ref._update()
      
      return this._super.apply(this, arguments)
    },

    /**
     * private methods
     */

    _setCategory: function (ev) {
      ev.preventDefault()
      var ref = this;
      var $target = $(ev.currentTarget)

      if (!$target.hasClass('active')) {
        ref.$dropdownItems.each(function () {
          $(this).removeClass('active')
        })
        $target.addClass('active')
      }

      // active category has changed, update search modal
      ref._update()
    },

    /**
     * must be called after $dropdownItems, $indicator and $form are defined
     */
    _update: function () {
      var ref = this;
      var $activeCategory = ref.$dropdownItems.filter(function (_) { return $(this).hasClass('active') })

      if ($activeCategory) {
        // update search path
        var searchPath = $activeCategory.attr('href')
        ref.$form.attr('action', searchPath)

        // update indicator
        ref.$indicator.text($activeCategory.text())
      }
    },
  })
})