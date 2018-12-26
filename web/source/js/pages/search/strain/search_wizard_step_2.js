'use strict';

W.ns('W.pages.search.vt');

W.pages.search.vt.SearchWizardStep2 = W.pages.search.vt.SearchWizardStep.extend({

    selectedEffects: [],
    renderData: {},

    init: function init(options) {
        this._super({
            step: 2,
            model: options && options.model,
            currentUserId: options && options.currentUserId,
            submit_el: '.btn-step-2',
            skip_el: '.btn-skip-2',
            back_el: '.btn-go-back',
            template_el: '#search-wizard-step2'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickVtEffect(this.selectedEffects);
        this.clickRemoveEffect(this.selectedEffects)
    },

    renderHTML: function renderHTML() {
        return this.$template(this.renderData);
    },

    submit: function submit() {
        var that = this;
        this.showDialogOrProceed(this.selectedEffects, function () {
            var data = {step: that.step, data: {effects: that.selectedEffects}};
            window.history.pushState(data, 'search-step-2', '/search/vt/wizard/#3');
            $.publish('update_step_data', data);
            $.publish('show_step', {step: 3});
        });
    },

    skip: function skip() {
        var data = {step: this.step, data: {skipped: true}};
        window.history.pushState(data, 'search-step-2', '/search/vt/wizard/#3');
        $.publish('update_step_data', data);
        $.publish('show_step', {step: 3});
    },

    back: function back() {
        $.publish('update_step_data', {step: this.step, data: {effects: this.selectedEffects}});
        $.publish('show_refreshed_step', {step: 1});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            this.restoreEffectsState(this.step, this.selectedEffects);
        }
    }

});