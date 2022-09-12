
odoo.define('do_customization.faq.search', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');

    publicWidget.registry.faqSearch = publicWidget.Widget.extend({
    selector: '#faq-search',
    events: {
//      'keypress input[type="text"]': '_pressEnterKey',
//      'mouseenter .input-group-append button': '_mouseenter'
        'click .faq_search_btn': '_search',
    },

    start: function () {
      var textBox = $("#faq-search input[type='text']");
//      var searchMobile = $("#xtremo_mobile_menu .col-sm-12 .fa-search");
      textBox.on('keypress', this._getSearch);
    },

    _search: function () {
      var $target = this.$target;
      var searchString = $target.find("input[type='text']").val();
      if (searchString.length > 0){
        let url = `/faq?search=${searchString}`;

        window.location.href = url;
//        document.getElementById("faq-search-box").value = searchString;
      }
      else {
        let url = '/faq'
        window.location.href = url;
      }
    },

    _getSearch: function (ev) {
      var bool = ev.currentTarget.classList.contains("fa-search");
      var searchString = "";
      if (bool) {
        var searchString = $("#faq-search input[type='text']").val();
      } else if (ev.keyCode === 13) {
        var searchString = ev.currentTarget.value;
      }
      if (searchString.length > 0){
        window.location.href = `/faq?search=${searchString}`;
      }
    },

  });

});