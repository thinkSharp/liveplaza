/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('marketplace_facebook_live_stream.mp_live_stream', function(require) {
    "use strict";

    $(document).ready(function(){
        var page_url = window.location.href
        var carousel_items;
        if (page_url.indexOf("seller/shops/list") > -1){
            carousel_items = 3
        }
        else if (page_url.indexOf("/seller/profile") > -1 || page_url.indexOf("seller/shop") > -1){
            carousel_items = 1
        }else{
            carousel_items = 3
        }
        console.log('carousel_items'+carousel_items)


        // $('.live_stream_owl_carousel').owlCarousel({
        //     items: carousel_items,
        //     navigation : true,
        //     pagination: false,
        //     slideSpeed: 500,
        //     autoPlay: false,
        //     stopOnHover : true,
        //     navigationText: ["<i class='fa fa-angle-double-left fa-2x'></i>","<i class='fa fa-angle-double-right fa-2x'></i>"],
        //     // autoWidth:false,
        //     singleItem:false,
        //     loop:true,

        // });

        $(".live_stream_owl_carousel").owlCarousel({
            items: carousel_items,
            // loop: true,
            dots: false,
            nav: true,
            responsive: {
              0: {
                items: 1,
              },
              576: {
                items: 2,
              },
              786: {
                items: 4,
              },
            },
          });

          $(".live_stream_owl_carousel_x").owlCarousel({
            items: carousel_items,
            // loop: true,
            dots: false,
            nav: true,
            navText: ["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
            responsive: {
              0: {
                items: 1,
              },
              576: {
                items: 1,
              },
              786: {
                items: 1,
              },
            },
          });

        $(".wk_upcoming_live_stream").on('click', function(){
            var stream_start_datetime= $(this).find("#stream_start_datetime").text()
            $("#wk_upcoming_stream_modal .stream_scheduled_datetime").html(' ' + '<b>' + moment(stream_start_datetime).format('LT') + '</b>' + ' on ' + '<b>' + moment(stream_start_datetime).format('L') + '</b>');
            $("#wk_upcoming_stream_modal").modal('show')
        })


    });


});
