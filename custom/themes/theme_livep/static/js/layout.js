odoo.define('livep.layout', ['xtremo.shop.advance.search', 'web.public.widget'], function (require) {
  "use strict";

  var publicWidget = require('web.public.widget');

  publicWidget.registry.autohideMenu = publicWidget.registry.autohideMenu.extend({

    /**
     * @override
     * We don't want xtremo to set top margin of the main
     */
    set_header: function () {}

  });

})
