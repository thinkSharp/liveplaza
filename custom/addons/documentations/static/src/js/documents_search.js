
odoo.define('documentations.documents.search', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');

    publicWidget.registry.docSearch = publicWidget.Widget.extend({
    selector: '.docs_wrapper',
    events: {
        'click .doc_search_btn': '_search',
        'keypress input[type="text"]': '_getSearch',
        'click .doc_search_category': '_filterSearch',
    },

    start: function () {
      var textBox = $("#doc-search-box input[type='text']");
      var textBoxMobile = $("#doc-search-box input[type='text']");
//      var searchMobile = $("#xtremo_mobile_menu .col-sm-12 .fa-search");
      textBox.on('keypress', this._search);
    },

    _filterSearch: function(e) {
        var li = $(e.currentTarget).parents('li');
        var filter = li.data('filter-category');
        var filter_id = li.data('filter-category-id');
        var url = window.location.href;

        if (url.indexOf("&") > 0) {
	        var url = url.substring(0, url.indexOf("&"));
	    }

        if(filter.length == 0) {
            window.location.href = url;
        }
        else {
            var filter_url = url + `&search_filter=${filter_id}_${filter}`;
            window.location.href = filter_url;
        }

    },

    _search: function () {
      var $target = this.$target;
      var searchString = $target.find("input[type='text']").val();
      if (searchString.length > 0){
        let url = `/user_guides?search=${searchString}`;

        window.location.href = url;
//        document.getElementById("doc-search-box").value = searchString;
      }
      else {
        let url = '/user_guides'
        window.location.href = url;
      }
    },

    _getSearch: function (ev) {
      var bool = ev.currentTarget.classList.contains("fa-search");
      var searchString = "";
      if (bool) {
        var searchString = $("#doc-search-box input[type='text']").val();
      } else if (ev.keyCode === 13) {
        var searchString = ev.currentTarget.value;
      }
      if (searchString.length > 0){
        window.location.href = `/user_guides?search=${searchString}`;
      }
    },

  });

});