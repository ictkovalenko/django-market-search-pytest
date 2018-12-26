'use strict';

W.ns('W.pages.search.vt');

W.pages.search.vt.SearchWizardStep4 = W.pages.search.vt.SearchWizardStep.extend({

    selectedSideEffects: [],
    renderData: {},

    init: function init(options) {
        this._super({
            step: 4,
            model: options && options.model,
            currentUserId: options && options.currentUserId,
            submit_el: '.btn-step-4',
            skip_el: '.btn-skip-4',
            back_el: '.btn-go-back',
            template_el: '#search-wizard-step4'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickVtEffect(this.selectedSideEffects);
        this.clickRemoveEffect(this.selectedSideEffects)
    },

    renderHTML: function renderHTML() {
        return this.$template({
            side_effects: this.renderData.side_effects,
            isEnabled: this.isEnabled.bind(this)
        });
    },

    submit: function submit() {
        var that = this;
        this.showDialogOrProceed(this.selectedSideEffects, function () {
            $.publish('update_step_data', {step: that.step, data: {effects: that.selectedSideEffects}});
            $.publish('submit_form', that.model.getData());
        });
    },

    skip: function skip() {
        $.publish('update_step_data', {step: this.step, data: {skipped: true}});
        $.publish('submit_form', this.model.getData());
    },

    back: function back() {
        $.publish('update_step_data', {step: this.step, data: {effects: this.selectedSideEffects}});
        $.publish('show_refreshed_step', {step: 3});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            this.restoreEffectsState(this.step, this.selectedSideEffects);
        }
    },

    isEnabled: function isEnabled(sideEffect) {
        if (sideEffect.data_name !== 'hungry') {
            return { value: true };
        }

        var effects = this.model.data[2].effects;
        var hasHungerEffect = _.find(effects, function(effect) {
            return effect.name === 'hungry';
        });

        var medicalBenefits = this.model.data[3].effects;
        var hasAppetiteBenefit = _.find(medicalBenefits, function(effect) {
            return effect.name === 'restore_appetite';
        });

        if (!hasHungerEffect && ! hasAppetiteBenefit) {
            return { value: true };
        } else if (hasHungerEffect && hasAppetiteBenefit) {
            return { value: false, reason: 'You cannot minimize this side effect because ' +
                    'you selected Hungry as a desired effect and Restore Appetite as medical benefit.' };
        } else if (hasHungerEffect) {
            return { value: false, reason: 'You cannot minimize this side effect because ' +
                    'you selected Hungry as a desired effect.' };
        } else if (hasAppetiteBenefit) {
            return { value: false, reason: 'You cannot minimize this side effect because ' +
                    'you selected Restore Appetite as medical benefit.' };
        }

        return { value: true };
    }

});