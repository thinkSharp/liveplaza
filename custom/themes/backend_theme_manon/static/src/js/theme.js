/*!
 # -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
 */

odoo.define('backend_theme_manon.theme_manon', function(require) {
    "use strict";

    var session = require('web.session');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var session = require('web.session');
    var ThemeSlider = Widget.extend({
        template: 'ThemeSlider',
        events: {
            "click .oe_theme_button": "render_dropdown",
            "click .o_filter_button": "on_click_filter_button",
            "click .theme_item": 'change_theme',
        },
        start: function() {
            this._super();
            this.$filter_buttons = this.$('.o_filter_button');
            this.$wk_color_button = this.$('.wk_color_button');
            this.$wk_font_button = this.$('.wk_font_button');
            this.$wk_extra_button = this.$('.wk_extra_button');
            this.$filter = 'color';
            this.$theme_preview = this.$('.o_mail_navbar_dropdown_channels');
            this.$dropdown = this.$(".js_theme_dropdown");
        },
        is_open: function() {
            return this.$el.hasClass('open');
        },
        update_channels_preview: function () {
            var self = this;
            this.$theme_preview.empty();
            var filter = this.filter == undefined ? 'color' : this.filter ;

            if (filter == 'color') {
                rpc.query({
                    model:'wk.backend.color',
                    method:'search_read',
                    args:[[]],
                })
                .then(function(colors){
                    var dropdown_content = QWeb.render('ThemeSlider.Colors', {
                        widget: self,
                        active_view: self.active_view,
                        view: self.view,
                        colors: colors,
                    });
                    $(dropdown_content).appendTo(self.$theme_preview);
                });
            }
            else if(filter == 'font') {
                rpc.query({
                    model: 'wk.backend.font',
                    method: 'search_read',
                    args:[[]],
                })
                .then(function(fonts){
                    var dropdown_content = QWeb.render('ThemeSlider.Fonts', {
                        widget: self,
                        active_view: self.active_view,
                        view: self.view,
                        fonts:fonts,
                    });
                $(dropdown_content).appendTo(self.$theme_preview);
                });
            }
        },
        on_click_filter_button: function (event) {
            event.stopPropagation();
            this.$filter_buttons.removeClass('o_selected');
            var $target = $(event.currentTarget);
            $target.addClass('o_selected');
            this.filter = $target.data('filter');
            this.update_channels_preview();
        },
        render_dropdown: function() {
            this.update_channels_preview();
        },
        make_scss_custo: function(url, value, type, id) {
            var self = this;
            self._rpc({
                route: '/theme/manon/make_scss_custo',
                params: {
                    'url': url,
                    'values': value,
                    'style_type': type,
                    'id': id,
                },
            }).then(function() {
                self._rpc({
                    route: '/manon/theme_customize',
                    params: {
                        get_bundle: true,
                    },
                }).then(function (bundles) {
                    var $allLinks = $();
                    var defs = _.map(bundles, function (bundleURLs, bundleName) {
                        var $links = $('link[href*="' + bundleName + '"]');
                        $allLinks = $allLinks.add($links);
                        var $newLinks = $();
                        _.each(bundleURLs, function (url) {
                            $newLinks = $newLinks.add($('<link/>', {
                                type: 'text/css',
                                rel: 'stylesheet',
                                href: url,
                            }));
                        });

                        var linksLoaded = new Promise(function (resolve, reject) {
                            var nbLoaded = 0;
                            $newLinks.on('load', function () {
                                if (++nbLoaded >= $newLinks.length) {
                                    resolve();
                                }
                            });
                            $newLinks.on('error', function () {
                                reject();
                                window.location.hash = 'theme=true';
                                window.location.reload();
                            });
                        });
                        $links.last().after($newLinks);
                        return linksLoaded;
                    });
                    return Promise.all(defs).then(function () {
                        $allLinks.remove();
                    }).guardedCatch(function () {
                        $allLinks.remove();
                    });
                }).then(function () {
                    // Some public widgets may depend on the variables that were
                    // customized, so we have to restart them.
                    self.trigger_up('widgets_start_request');
                });
            });
        },
        change_theme: function (evt) {
            var self = this;
            const $currentTarget = $(evt.currentTarget);
            let type = $currentTarget.attr('data-type') == 'color' ? 'color' : 'font';
            var baseURL, url;
            if ( type == 'color' ) {
                let values = {};
                baseURL = '/backend_theme_manon/static/src/scss/colors/';
                url = _.str.sprintf('%smanon_primary_variables.scss', baseURL);
                let primary_color = $currentTarget.attr('data-primary_color_value');
                let id = $currentTarget.attr('data-color_id');
                self.make_scss_custo(url, primary_color, type, id);
            } else {
                baseURL = '/backend_theme_manon/static/src/scss/fonts/';
                url = _.str.sprintf('%sfonts.scss', baseURL);
                let font = $currentTarget.attr('data-font_value');
                let id = $currentTarget.attr('data-font_id');
                self.make_scss_custo(url, font, type, id);
            }
         },
    });

    if ( session.is_system ) {
        SystrayMenu.Items.push(ThemeSlider);
    }

    $(document).ready(function() {

        $(document).on('click','.theme_item.color',function(){
            $(this).closest('.row').find('.check').remove();
            $(this).append("<i class='check fa fa-check-circle-o'/>");
        });

        $(document).on('click','.theme_item.font',function(){
            $(this).closest('.row').find('.check').remove();
            $(this).prepend("<i class='check fa fa-check-circle-o'/>");
        });

    });
});
