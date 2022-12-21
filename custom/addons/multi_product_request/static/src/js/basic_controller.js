odoo.define('multi_product_request.BasicController', function (require) {
"use strict";

/**
 * The BasicController is mostly here to share code between views that will use
 * a BasicModel (or a subclass).  Currently, the BasicViews are the form, list
 * and kanban views.
 */

var AbstractController = require('web.AbstractController');
var core = require('web.core');
var Dialog = require('web.Dialog');
var FieldManagerMixin = require('web.FieldManagerMixin');
var Pager = require('web.Pager');
var TranslationDialog = require('web.TranslationDialog');
var _t = core._t;

var BasicController = require('web.BasicController');


BasicController.include ({

    custom_events: _.extend({}, AbstractController.prototype.custom_events, FieldManagerMixin.custom_events, {
        discard_changes: '_onDiscardChanges',
        reload: '_onReload',
        resequence_records: '_onResequenceRecords',
        set_dirty: '_onSetDirty',
        load_optional_fields: '_onLoadOptionalFields',
        save_optional_fields: '_onSaveOptionalFields',
        sidebar_data_asked: '_onSidebarDataAsked',
        translate: '_onTranslate',
    }),

    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this.archiveEnabled = params.archiveEnabled;
        this.confirmOnDelete = params.confirmOnDelete;
        this.hasButtons = params.hasButtons;
        FieldManagerMixin.init.call(this, this.model);
        this.mode = params.mode || 'readonly';
        this.handle = this.initialState.id;
        // savingDef is used to ensure that we always wait for pending save
        // operations to complete before checking if there are changes to
        // discard when discardChanges is called
        this.savingDef = Promise.resolve();
        this.viewId = params.viewId;
        var self = this;

        var action = '';
        var view = '';
        var model = '';
        var url = window.location.hash;
        var split = url.split('&');
        for(var i = 0 ; i < split.length ; i++) {
            if(split[i].includes('action')) {
                action = split[i];
            }
            if(split[i].includes('view_type')) {
                view = split[i];
            }
            if(split[i].includes('model')) {
                model = split[i];
            }
        }

        var get_id = action.split('=');
        var view_type = view.split('=');

        if(get_id.length > 1 && view_type.length > 1 && model.length > 1) {
            var action_id = parseInt(get_id[1])
            if(action_id > 0 && model[1] == 'product.request' && view_type[1] == 'form') {
                window.onbeforeunload = function (e) {
                    e.preventDefault();
                    e.returnValue = 'Are you sure you want to close?'
                    if(window.onbeforeunload != null) {
                        self._rpc({
                            model: 'product.request',
                            method: 'reload',
                            args: [action_id],
                        })
                        .then(function (result) {
                            window.onbeforeunload = null;
    //                                if(result) {
    //                                    window.location.href = result;
    //                                }
                        });
                    }
                }
            }
        }
    },
});

return BasicController;
});