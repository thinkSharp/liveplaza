odoo.define('documentations.FormController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var core = require('web.core');
    var qweb = core.qweb;
    var FormController = require('web.FormController');

    FormController.include({

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);

            this.actionButtons = params.actionButtons;
            this.disableAutofocus = params.disableAutofocus;
            this.footerToButtons = params.footerToButtons;
            this.defaultButtons = params.defaultButtons;
            this.hasSidebar = params.hasSidebar;
            this.toolbarActions = params.toolbarActions || {};
        },

        _getDocument: function(parentID) {
            var self = this;
            var url = window.location.hash;
            var split = url.split('&');
            for(var i = 0 ; i < split.length ; i++) {
                if(split[i].includes('action')) {
                    var get_id = split[i].split('=');
                    if(get_id.length > 1) {
                        var action_id = parseInt(get_id[1])
                        if(action_id > 0) {
                            this._rpc({
                                route: "/user_guides/link_action",
                                params: {
                                    action_id: action_id,
                                },
                            })
                            .then(function (result) {
                                if(result) {
                                    window.location.href = result;
                                }
                            });
                        }
                    }
                }
            }
        },

        renderButtons: function ($node) {
            var $footer = this.footerToButtons ? this.renderer.$('footer') : null;
            var mustRenderFooterButtons = $footer && $footer.length;
            if (!this.defaultButtons && !mustRenderFooterButtons) {
                return;
            }
            this.$buttons = $('<div/>');
            if (mustRenderFooterButtons) {
                this.$buttons.append($footer);

            } else {
                this.$buttons.append(qweb.render("FormView.buttons", {widget: this}));
                this.$buttons.on('click', '.o_form_button_edit', this._onEdit.bind(this));
                this.$buttons.on('click', '.o_form_button_create', this._onCreate.bind(this));
                this.$buttons.on('click', '.o_form_button_document', this._getDocument.bind(this));
                this.$buttons.on('click', '.o_form_button_save', this._onSave.bind(this));
                this.$buttons.on('click', '.o_form_button_cancel', this._onDiscard.bind(this));
                this._assignSaveCancelKeyboardBehavior(this.$buttons.find('.o_form_buttons_edit'));
                this.$buttons.find('.o_form_buttons_edit').tooltip({
                    delay: {show: 200, hide:0},
                    title: function(){
                        return qweb.render('SaveCancelButton.tooltip');
                    },
                    trigger: 'manual',
                });
                this._updateButtons();
            }
            this.$buttons.appendTo($node);
        },

    });

    return FormController;
});

odoo.define('documentations.ListController', function (require) {
    "use strict";
    var core = require('web.core');
    var config = require('web.config');
    var BasicController = require('web.BasicController');
    var qweb = core.qweb;

    var ListController = require('web.ListController');
    ListController.include({
        buttons_template: 'ListView.buttons',

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.hasSidebar = params.hasSidebar;
            this.toolbarActions = params.toolbarActions || {};
            this.editable = params.editable;
            this.noLeaf = params.noLeaf;
            this.selectedRecords = params.selectedRecords || [];
            this.multipleRecordsSavingPromise = null;
            this.fieldChangedPrevented = false;
        },

        _getDocument: function(parentID) {
            var self = this;
            var url = window.location.hash;
            var split = url.split('&');
            for(var i = 0 ; i < split.length ; i++) {
                if(split[i].includes('action')) {
                    var get_id = split[i].split('=');
                    if(get_id.length > 1) {
                        var action_id = parseInt(get_id[1])
                        if(action_id > 0) {
                            this._rpc({
                                route: "/user_guides/link_action",
                                params: {
                                    action_id: action_id,
                                },
                            })
                            .then(function (result) {
                                if(result) {
                                    window.location.href = result;
                                }
                            });
                        }
                    }
                }
            }

        },

        renderButtons: function ($node) {
            if (!this.noLeaf && this.hasButtons) {
                this.$buttons = $(qweb.render(this.buttons_template, {widget: this}));
                this.$buttons.on('click', '.o_list_button_add', this._onCreateRecord.bind(this));

                this._assignCreateKeyboardBehavior(this.$buttons.find('.o_list_button_add'));
                this.$buttons.find('.o_list_button_add').tooltip({
                    delay: {show: 200, hide: 0},
                    title: function () {
                        return qweb.render('CreateButton.tooltip');
                    },
                    trigger: 'manual',
                });
                this.$buttons.on('mousedown', '.o_list_button_discard', this._onDiscardMousedown.bind(this));
                this.$buttons.on('click', '.o_list_button_discard', this._onDiscard.bind(this));
                this.$buttons.on('click', '.o_list_button_document', this._getDocument.bind(this));
                this.$buttons.find('.o_list_export_xlsx').toggle(!config.device.isMobile);
                this.$buttons.appendTo($node);
            }
        },

        });

    return ListController;
});


//odoo.define('documentations.SwitchCompanyMenu', function(require) {
//"use strict";
//
//var config = require('web.config');
//var core = require('web.core');
//var session = require('web.session');
//var SystrayMenu = require('web.SystrayMenu');
//var Widget = require('web.Widget');
//
//var _t = core._t;
//var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
//var SwitchCompanyMenu = SwitchCompanyMenu.extend({
//    template: 'SwitchCompanyMenu',
//    events: {
//        'click .dropdown-item[data-menu] div.log_into': '_onSwitchCompanyClick',
//        'keydown .dropdown-item[data-menu] div.log_into': '_onSwitchCompanyClick',
//        'click .dropdown-item[data-menu] div.toggle_company': '_onToggleCompanyClick',
//        'keydown .dropdown-item[data-menu] div.toggle_company': '_onToggleCompanyClick',
//        'click .o_menu_button_document': '_getDocument',
//    },
//    /**
//     * @override
//     */
//    init: function () {
//        this._super.apply(this, arguments);
//        this.isMobile = config.device.isMobile;
//        this._onSwitchCompanyClick = _.debounce(this._onSwitchCompanyClick, 1500, true);
//    },
//
//    _getDocument: function() {
//        alert("hello");
//        var self = this;
//        var url = window.location.hash;
//        var split = url.split('&');
//        for(var i = 0 ; i < split.length ; i++) {
//            if(split[i].includes('action')) {
//                var get_id = split[i].split('=');
//                if(get_id.length > 1) {
//                    var action_id = parseInt(get_id[1])
//                    if(action_id > 0) {
//                        this._rpc({
//                            route: "/user_guides/link_action",
//                            params: {
//                                action_id: action_id,
//                            },
//                        })
//                        .then(function (result) {
//                            if(result) {
//                                window.location.href = result;
//                            }
//                        });
//                    }
//                }
//            }
//        }
//
//    },
//
//    /**
//     * @override
//     */
//    willStart: function () {
//        var self = this;
//        this.allowed_company_ids = String(session.user_context.allowed_company_ids)
//                                    .split(',')
//                                    .map(function (id) {return parseInt(id);});
//        this.user_companies = session.user_companies.allowed_companies;
//        this.current_company = this.allowed_company_ids[0];
//        this.current_company_name = _.find(session.user_companies.allowed_companies, function (company) {
//            return company[0] === self.current_company;
//        })[1];
//        return this._super.apply(this, arguments);
//    },
//
//    //--------------------------------------------------------------------------
//    // Handlers
//    //--------------------------------------------------------------------------
//
//    /**
//     * @private
//     * @param {MouseEvent|KeyEvent} ev
//     */
//    _onSwitchCompanyClick: function (ev) {
//        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
//            return;
//        }
//        ev.preventDefault();
//        ev.stopPropagation();
//        var dropdownItem = $(ev.currentTarget).parent();
//        var dropdownMenu = dropdownItem.parent();
//        var companyID = dropdownItem.data('company-id');
//        var allowed_company_ids = this.allowed_company_ids;
//        if (dropdownItem.find('.fa-square-o').length) {
//            // 1 enabled company: Stay in single company mode
//            if (this.allowed_company_ids.length === 1) {
//                if (this.isMobile) {
//                    dropdownMenu = dropdownMenu.parent();
//                }
//                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
//                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
//                allowed_company_ids = [companyID];
//            } else { // Multi company mode
//                allowed_company_ids.push(companyID);
//                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
//            }
//        }
//        $(ev.currentTarget).attr('aria-pressed', 'true');
//        session.setCompanies(companyID, allowed_company_ids);
//    },
//
//    //--------------------------------------------------------------------------
//    // Handlers
//    //--------------------------------------------------------------------------
//
//    /**
//     * @private
//     * @param {MouseEvent|KeyEvent} ev
//     */
//    _onToggleCompanyClick: function (ev) {
//        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
//            return;
//        }
//        ev.preventDefault();
//        ev.stopPropagation();
//        var dropdownItem = $(ev.currentTarget).parent();
//        var companyID = dropdownItem.data('company-id');
//        var allowed_company_ids = this.allowed_company_ids;
//        var current_company_id = allowed_company_ids[0];
//        if (dropdownItem.find('.fa-square-o').length) {
//            allowed_company_ids.push(companyID);
//            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
//            $(ev.currentTarget).attr('aria-checked', 'true');
//        } else {
//            allowed_company_ids.splice(allowed_company_ids.indexOf(companyID), 1);
//            dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
//            $(ev.currentTarget).attr('aria-checked', 'false');
//        }
//        session.setCompanies(current_company_id, allowed_company_ids);
//    },
//
//});
//
//if (session.display_switch_company_menu) {
//    SystrayMenu.Items.push(SwitchCompanyMenu);
//}
//
//return SwitchCompanyMenu;
//
//});

