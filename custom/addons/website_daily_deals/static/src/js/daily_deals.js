odoo.define("website_daily_deals.daily_deals_js", function (require) {
"use strict";

    var ajax = require('web.ajax');

    function initializeNestedCarousel () {
        $(".owl-carousel--nested").owlCarousel({
        nav: true,
        dots: true,
        autoplay: false,
        loop: false,
        items: 5,
        dots:true,
        autoWidth: false,
        navText: ["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
        responsive:{
                0:{
                    items:2
                    },
                480:{
                    items:2
                },
                768 : {
                    items:3
                },
                998 : {
                    items:5
                }
            }
        });
    }

    $(document).ready(function() {

		var deal_options = {
			autoplay:true,
			items:1,
			nav:true,
            dots:true,
            smartSpeed:800,
            autoplayTimeout: 5000,
            autoplayHoverPause: true,
            navText: ["<i class='deal-left-right fa fa-angle-left'></i>","<i class='deal-left-right fa fa-angle-right'></i>"],
            autoWidth:false,
            thumbs: true,
            thumbsPrerendered: true,
            mouseDrag: true,
            touchDrag: true,
            items: 1,
            onInitialized: initializeNestedCarousel,
		}

        $(".daily_deals_owl_carousel").owlCarousel(deal_options);

        function startCarouselAutoplay () {
            $(".daily_deals_owl_carousel").trigger('play.owl.autoplay');
        }

        function stopCarouselAutoplay () {
            $(".daily_deals_owl_carousel").trigger('stop.owl.autoplay');
        }

        $(".daily_deals_owl_carousel").on('touchstart', stopCarouselAutoplay);
        // owl restart autoplay internally when touchend, calling to start again here makes weired side effects

        $(".deal_main_div").each(function(){
            var end_date= $(this).find("input[name='end_date']").val();
            end_date = new Date(end_date)
            end_date.setHours(23, 59, 59)
            var deal_id = parseInt($(this).find("input[name='deal_id']").val(),10);
            var state = $(this).find("input[name='state']").val()
            var msg_before_offset= $(this).find("input[name='msg_before_offset']").val()
            if (state=="validated") {
                $(this).find(".deal_countdown_timer").countdown({
                    date: end_date,
                    offset: +6.5,
                    day: 'day',
                    days: 'day',
                    hour:   'hrs',
                    hours: 'hrs',
                    minute: 'min',
                    minutes:'min',
                    seconds:'sec',
                    second:'sec',
                },
                function () {
                    window.location.reload();
                });
                if(msg_before_offset){
                    var $target = $(this).find(".msg_before_exp");
                    $(this).find(".expiry_messages").countdown({
                        date: msg_before_offset,
                        offset: +0,
                        day: 'Day',
                        days: 'Days'
                    },function () {
                        $target.css('visibility','visible');
                    });
                }

            }
        });

        $('.deal_product_quick_view').on('click',function(){
            var product_tmpl_id     = parseInt($(this).attr('product-template-id'));
            var product_variant_id  = parseInt($(this).attr('product-product-id'));
            var url = "/shop/product/"+product_tmpl_id
            if (product_tmpl_id){
                stopCarouselAutoplay()
                $.get(url, {}, function (data){
                    if (data) {
                        data = $(data).find("#product_detail");
                        $('#deal_product_item_view_modal').modal('show');
                        $('#deal_product_item_view_modal .modal-body').html(data);
                        $('#deal_product_item_view_modal').find("#product_detail>.row:nth-child(1)").hide();
                    } else {
                        startCarouselAutoplay()
                    }
                }).fail(startCarouselAutoplay)
            }
        });

        $('#deal_product_item_view_modal').on('hidden.bs.modal', startCarouselAutoplay)
    });

});
