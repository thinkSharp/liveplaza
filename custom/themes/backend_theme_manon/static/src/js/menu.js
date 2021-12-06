/*!
 # -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
*/

odoo.define('backend_theme_manon.Menu', function (require) {
"use strict";

    var Menu = require('web.Menu');
    var session = require('web.session');
    var id = session.uid;

    Menu.include({
        events: _.extend({
            'click .o_menu_apps': '_render_dropdown_menus',
            'click .sub_menu': '_render_sub_menus',
            'click .sub_mobile_view': '_disable_view',
            'click .o_menu_sections a': '_add_dropdown_anim',
            // 'click .fa-bars': '_rise_menu',
            // 'click .o_menu_sections > li > .dropdown-menu > a': '_collapse_menu',
            // 'click .o_menu_sections > li > a': '_change_icon',
        }, Menu.prototype.events),
        start: function() {
            this._super.apply(this, arguments);
            var ul = this.$el.find('.o_menu_sections');
        },
        _render_dropdown_menus: function(evt) {
            var self = this;
            var $target = $(evt.currentTarget);
            if ( $(window).width() <= 767 ) {
                $target.addClass('mobile');
            }
            if ($target.find('.dropdown-menu').hasClass('show') ) {
                $target.find('.mobile_view').remove();
            } else {
                $target.find('.dropdown-menu').after('<div class="mobile_view"></div>');
            }
        },
        _render_sub_menus: function(evt) {
            var self = this;
            var $target = $(evt.currentTarget);
            $target.siblings('.o_menu_sections').addClass('active');
            let $anchor = $('.o_menu_sections li a.o-no-caret');
            $anchor.find('.wk_plus').remove();
            $anchor.append('<i class="wk_plus"></i>')
            $target.parent().append('<div class="sub_mobile_view"></div>');
        },
        _disable_view: function(evt) {
            var self = this;
            var $target = $(evt.currentTarget);
            $target.siblings('.o_menu_sections').removeClass('active');
                $target.remove();
        },
        _add_dropdown_anim: function(evt) {
            var $target = $(evt.currentTarget);
            if ( $target.attr('href') != '#' ) {
                $('.sub_mobile_view').trigger('click');
            } else {
                let $wk_plus = $target.find('.wk_plus');
                if ( $wk_plus.hasClass('active') ) {
                    $wk_plus.removeClass('active');
                } else {
                    $wk_plus.addClass('active');
                }
            }

        },
        // _rise_menu: function(evt) {
        //     const ul_container = $(evt.target).parent().parent();
        //     if(ul_container.find('.top-menu-show').length > 0) {
        //         ul_container.children().removeClass('top-menu-show');
        //     }
        //     else {
        //         let o_menu_sections = ul_container.find('.o_menu_sections');
        //         if (o_menu_sections.children().length > 0) {
        //             o_menu_sections.addClass('top-menu-show');
        //             ul_container.find('.o_menu_sections li').each(function() {
        //                 if($(this).find('.dropdown-menu').length > 0) {
        //                     $(this).children('a').removeClass('dropdown-toggle').addClass('wk-dropdown-icon');
        //                 }
        //             })
        //         }
        //     }
        // },
        // _collapse_menu: function(evt) {
        //     $(evt.target).parents('.o_menu_sections').removeClass('top-menu-show');
        // },
        // _change_icon: function(evt) {
        //     let self = $(evt.target);
        //     if(self.hasClass('wk-dropdown-icon-right')) {
        //         self.removeClass('wk-dropdown-icon-right');
        //         self.addClass('wk-dropdown-icon');
        //     }
        //     else {
        //         self.removeClass('wk-dropdown-icon').addClass('wk-dropdown-icon-right');
        //     }
        // }
    });

    // publicWidget.registry.websiteSaleCartLink = publicWidget.Widget.extend({
    //     selector: '.o_main_navbar',
    //     events: {
    //         'click .o_menu_apps': '_render_dropdown',
    //     },
    //     start: function() {
    //         console.log('----');
            
    //     },
    //     _render_dropdown: function(evt) {
    //         console.log('asdsadasdasd');
    //     }
    // });

});
