'use strict';

W.ns('W.pages.search.vt');

W.pages.search.vt.SearchWizardStep3 = W.pages.search.vt.SearchWizardStep.extend({

    selectedBenefits: [],
    renderData: {},

    init: function init(options) {
        this._super({
            step: 3,
            model: options && options.model,
            currentUserId: options && options.currentUserId,
            submit_el: '.btn-step-3',
            skip_el: '.btn-skip-3',
            back_el: '.btn-go-back',
            template_el: '#search-wizard-step3'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickVtEffect(this.selectedBenefits);
        this.clickRemoveEffect(this.selectedBenefits);

        if (this.isStepSkipped(2)) {
            $(this.submit_el).attr('disabled', 'disabled');
            $(this.skip_el).attr('disabled', 'disabled');
        }
    },

    renderHTML: function renderHTML() {
        return this.$template(this.renderData);
    },

    submit: function submit() {
        var that = this;
        this.showDialogOrProceed(this.selectedBenefits, function () {
            var data = {step: that.step, data: {effects: that.selectedBenefits}};
            window.history.pushState(data, 'search-step-3', '/search/vt/wizard/#4');
            $.publish('update_step_data', data);
            $.publish('show_step', {step: 4});
        });
    },

    skip: function skip() {
        var data = {step: this.step, data: {skipped: true}};
        window.history.pushState(data, 'search-step-3', '/search/vt/wizard/#4');
        $.publish('update_step_data', data);
        $.publish('show_step', {step: 4});
    },

    back: function back() {
        $.publish('update_step_data', {step: this.step, data: {effects: this.selectedBenefits}});
        $.publish('show_refreshed_step', {step: 2});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            this.restoreEffectsState(this.step, this.selectedBenefits);
        }
    }

});