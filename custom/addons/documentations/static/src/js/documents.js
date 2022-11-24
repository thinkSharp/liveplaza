

// left navigation bar in documentation page
$(document).ready(function () {
     var trigger = $('.hamburger');
     var isClosed = false;
     var navClosed = true;
     var width = 786;
     var right_btn = $('.right_nav_btn');
     if(window.screen.width > width) {
        isClosed = false;
     }
     else {
        isClosed = true;
     }

    var left_nav = document.getElementById('doc-left-nav');
    var left_nav_ul = $('.doc_left_nav_list');
    var right_nav_ul = $('.doc_right_nav_list');
    var content = document.getElementById('doc-content');
    var right_nav = document.getElementById('doc-right-nav');
    trigger.click(function () {
      hamburger_click(width);
    });
    right_btn.click(function(){
        right_nav_click(width);
    });

    // click the hamburger menu on left nav bar
    function hamburger_click(width) {
        if(window.screen.width > width) {
          if (isClosed == false) {
            trigger.removeClass('is-open');
            trigger.addClass('is-closed');
            left_nav.style.width = "50px";
            left_nav.style.minWidth = "50px";
            left_nav_ul.hide();
            content.style.marginLeft = "50px";
            isClosed = true;
          } else {
            trigger.removeClass('is-closed');
            trigger.addClass('is-open');
            left_nav_ul.removeClass('close');
            left_nav_ul.show();
            left_nav.style.width = "230px";
            content.style.marginLeft = "230px";
            isClosed = false;
          }
      }
        else {
            if (isClosed == false) {
                trigger.removeClass('is-open');
                trigger.addClass('is-closed');
                left_nav.style.width = "50px";
                left_nav.style.minWidth = "50px";
                left_nav.style.zIndex = "1";
                left_nav_ul.hide();
                $('#doc-right-nav').show();
                isClosed = true;
            } else {
                trigger.removeClass('is-closed');
                trigger.addClass('is-open');
                left_nav_ul.removeClass('close');
                left_nav_ul.show();
                left_nav.style.width = "100%";
                left_nav.style.zIndex = "999";
                $('#doc-right-nav').hide();
//                left_nav.style.maxWidth = "100%";

//                right_nav.style.marginLeft = "23%";
                isClosed = false;
            }
      }
  }

    function right_nav_click(width) {
        if(window.screen.width > width) {
            if (navClosed == false) {
                right_nav.style.width = "50px";
                content.style.marginRight = "50px";
                right_nav_ul.hide();
                navClosed = true;
            } else {
                right_nav.style.width = "220px";
                right_nav_ul.show();
                content.style.marginRight = "220px";
                navClosed = false;
            }
        }
        else {
            if (navClosed == false) {
                right_nav.style.width = "45px";
                content.style.marginRight = "45px";
                right_nav.style.zIndex = "1";
                right_nav_ul.hide();
                navClosed = true;
            } else {
                right_nav.style.width = "100%";
                right_nav.style.zIndex = "999";
                right_nav_ul.show();
                navClosed = false;
            }
        }
    }

  $('[data-toggle="offcanvas"]').click(function () {
        $('#docs-wrapper').toggleClass('toggled');
  });

});


// search bar in responsive
$(document).ready(function () {
    var search = false;

    $('.doc_search_btn_ph').click(function(){
        if (search == false) {
            $('.doc_search_outer2').show();
            search = true;
        }
        else {
            $('.doc_search_outer2').hide();
            search = false;
        }
    });
});


