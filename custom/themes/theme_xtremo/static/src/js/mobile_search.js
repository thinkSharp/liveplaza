odoo.define('livep.search.mobile', function(require) {
  "use strict";
  
  var publicWidget = require('web.public.widget')

  publicWidget.registry.LivvepMobileSearch = publicWidget.Widget.extend({
    selector: '.js-mobile-search',
    events: {
      "click .dropdown-item": "_handleCategoryChange",
    },

    /**
     * @override
     */

    start: function () {
      var ref = this;
      ref.$form = this.$el.find('form')
      ref.$indicator = this.$el.find('.category-indicator')
      ref.$dropdownItems = this.$el.find('.dropdown-item')

      var $defaultItem = ref._activeItemFromPath(window.location.pathname)
      if (!$defaultItem)
        $defaultItem = this.$el.find('.dropdown-item.active')
      ref.$activeItem = $defaultItem

      ref._updateDOM()
      
      return this._super.apply(this, arguments)
    },

    /**
     * handlers
     */

    _handleCategoryChange: function (ev) {
      ev.preventDefault()
      var ref = this;
      ref.$activeItem = $(ev.currentTarget)

      // active item has changed, update search modal
      ref._updateDOM()
    },

    /**
     * must be called after $dropdownItems, $indicator and $form are defined
     */
    _updateDOM: function () {
      var ref = this;

      // if no active item, do nothing
      if (!ref.$activeItem)
        return

      // update active class
      ref.$dropdownItems.each(function () {
        $(this).removeClass('active')
      })
      ref.$activeItem.addClass('active')

      // update search path
      var searchPath = ref.$activeItem.attr('href')
      ref.$form.attr('action', searchPath)

      // update indicator
      ref.$indicator.text(ref.$activeItem.text())
    },

    _pathEqual: function (path1, path2) {
      // url paths with '/' or without is equivalent in our case
      path1 = path1.replace(/\/$/, '')
      path2 = path2.replace(/\/$/, '')
      return path1 === path2
    },

    _activeItemFromPath: function (pathname) {
      var ref = this;
      var filtered = ref.$dropdownItems.filter(function () { return ref._pathEqual($(this).attr('href'), pathname) })
      return filtered.length !== 0 && filtered.first()
    },
  })
})
