'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizardStep2 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 2,
            model: options && options.model,
            submit_el: '.btn-b2c-step-2',
            template_el: '#b2c-wizard-2'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        $('.check').on('click', function (e) {
            $('.error-message').text('');
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({is_age_verified: stepData && stepData.is_age_verified});
    },

    validate: function validate() {
        var isAgeVerified = $('input[name="age"]').is(":checked");

        if (!isAgeVerified) {
            $('.error-message').text('Age verification is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {is_age_verified: $('input[name="age"]').is(":checked")};
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 3});
    }

});
