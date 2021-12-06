/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('xtremo.snippet.editor', function (require) {
  "use strict";
  var core = require('web.core');
  var ajax = require('web.ajax');
  var options = require('web_editor.snippets.options');
  var editor = require('web_editor.editor');
  var xtremo_core = require('xtremo.core');
  require('xtremo.website.beauty');
  var publicWidget = require('web.public.widget');





  options.registry.addXtremoBeauty = options.Class.extend({
    xmlDependencies: ['/theme_xtremo/static/src/xml/xtremo_beauty.xml'],
    start: function(){},
    addBeauty: function() {
      var $self = this.$target;
      var $item;
      if(this.$target.hasClass('frame-2')){
        $item = $(core.qweb.render('theme_xtremo.frame_2'));
      }else {
        $item = $(core.qweb.render('theme_xtremo.frame_1'));
      }
      $self.parent('.image-container').append($item);
    }
  });

    options.registry.xtremo_home_feature = options.Class.extend({
      start: function(){
        this.get_data(this.$target);
      },
      get_data: function($self){
        var calls = $self.data("ref");
        ajax.jsonRpc("/xtremo/get-feature", 'call', {"ref": calls})
         .then(function (data) {
            $self.html(data);
            xtremo_core.owl_for_home($self);
        })
      },

      cleanForSave: function () {
        this.$target.empty();
      }
    });

    options.registry.xtremo_team = options.Class.extend({

      addMore: function(){
        var item = this.$target.clone();
        this.$target.parent(".team").append(item);
      }
    });


    options.registry.conatct_us = options.Class.extend({

      onBuilt: function(){
        var href = window.location.pathname;

        if (href.includes("contactus")){
          this.$target.addClass("active");
          $("#wrap >.container").addClass("xtremo-contact-form");
          $("main").addClass("contact-us");
        } else{
          this.$target.remove();
          alert("This snippet supprts only for contact page");
        }
      },

      onRemove: function () {
        $("#wrap >.container").removeClass("xtremo-contact-form");
        $("main").removeClass("contact-us");
      },


    });

    editor.Class.include({
      save: function (reload) {
        $(".remove-ul").each(function() {$(this).empty();});
        $('.xtremo-beauty-modal').each(function() {$(this).remove();});
        $('.xtremo_home_feature').each(function() {$(this).empty();});
        $("main").removeClass("contact-us");
        $("#wrap >.container").removeClass("xtremo-contact-form");
        return this._super.apply(this, arguments);
      }
    });

})
