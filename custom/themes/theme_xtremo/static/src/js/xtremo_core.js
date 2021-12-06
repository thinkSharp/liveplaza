/* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */

odoo.define('xtremo.core', function (require) {
  "use strict";

  var list = {
    rtl: true,
    margin: 0,
    nav: true,
    loop: true,
    smartSpeed: 1000,
    navText: ["<i class='fa fa-angle-right'></i>","<i class='fa fa-angle-left'></i>"],
    responsive: {
      0: {
        items: 1
      },
      600: {
        items: 3
      },
      1000: {
        items: 5
      }
    }
  }

  function getId(id) {
    let element = document.getElementById(id);
    element = element == null ? false : element;
    return element;
  }

  function getQuery(query) {
    let element = document.querySelector(query);
    element = element == null ? false : element;
    return element;
  }

 function getClass(_class) {
    let element = document.getElementsByClassName(_class);
    element = element == null ? false : element;
    return element;
  }

  function get_resolve(funs) {
    funs.forEach(function(fun) {
      try {
        fun();
      } catch (e) {
        console.error("from xtremo core in : ",fun.name, " \n ",e);
      }
    })
  }

  function isMobile() {
    let width = window.screen.width;
    return (width > 767) ? false : true;
  }

  function _click(className, fun) {
    try {
      var classes = getClass(className);
      for (var i=0; i<classes.length; i++){
        classes[i].addEventListener("click",fun,false);
      }
    } catch (e) {
      console.error("Theme Xtremo : ",e);
    }
  }

  function owl_for_home($self){
    if( $self.find('.owl-carousel').length > 0){
      var ref = $self.find('.carousel-item');
      var con = ref.length > 5;
      list.loop = con ? true : false;
      list.rtl = con ? true : false;
      $self.find('.owl-carousel').owlCarousel(list);
    }
  }

  var response = {
    getId : getId,
    getClass : getClass,
    getQuery : getQuery,
    get_resolve : get_resolve,
    isMobile: isMobile,
    _click: _click,
    owl_for_home: owl_for_home
  }
  return response
//end tag
});
