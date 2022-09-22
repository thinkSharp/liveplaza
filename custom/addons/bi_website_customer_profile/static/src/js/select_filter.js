odoo.define('livep.select_filter', function (require) {
  'use strict';

  var publicWidget = require('web.public.widget')

  publicWidget.registry.selectFilter = publicWidget.Widget.extend({
    selector: '.js-select-filter',
    events: {
      'change': '_onFilterChange',
    },

    /**
     * @override
     */
    start: function () {
      var ref = this;
      ref._setup()
      ref._update()
      return ref._super.apply(ref, arguments)
    },

    //--------------------------------------------------------------------------------
    // Privates
    //--------------------------------------------------------------------------------

    _getTarget: function () {
      var ref = this;
      if (ref.$filterTarget)
        return ref.$filterTarget
      var targetID = ref.$el.data('target')
      ref.$filterTarget = $(`#${targetID}`)
      return ref.$filterTarget
    },

    _getCurrentFilter: function () {
      var ref = this;
      return ref.$el.find(':selected').data('filter')
    },

    _attachElements: function ($elements) {
      var ref = this;
      var $target = ref._getTarget()
      $elements.each(function() {
        $target.append($(this))
      })
    },

    _setup: function () {
      var ref = this;
      var $target = ref._getTarget()
      ref.$belongElements = ref.__getBelongElements($target)
    },

    _update: function () {
      var ref = this;
      ref.__prune(ref.$belongElements)
      var currentFilter = ref._getCurrentFilter()
      var $filteredElements = ref.__filter(currentFilter, ref.$belongElements)
      ref._attachElements($filteredElements)
    },

    //--------------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------------

    _onFilterChange: function () {
      var ref = this;
      ref.__selectReset(ref._getTarget())
      ref._update()
    },

    //--------------------------------------------------------------------------------
    // Helpers
    //--------------------------------------------------------------------------------

    __getBelongElements: function ($target) {
      return $target.children('[data-belong]')
    },

    __prune: function ($elements) {
      $elements.each(function () {
        $(this).detach()
      })
    },

    __filter: function (currentFilter, $elements) {
      if (!currentFilter)
        return $elements

      return $elements.filter(`[data-belong=${currentFilter}]`)
    },

    __selectReset: function ($selectElement) {
      $selectElement.val("")
    }
  })
})
