'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep1 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 1,
            model: options && options.model,
            submit_el: '.btn-b2b-step-1',
            template_el: '#b2b-wizard-1'
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({business_name: stepData && stepData.business_name});
    },

    validate: function validate() {
        var businessName = $('input[name="business_name"]').val();

        if (!businessName || businessName.trim().length === 0) {
            $('.error-message').text('Business name is required');
            return false;
        }

        if (businessName.length > 255) {
            $('.error-message').text('Max allowed length is 255 symbols');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {
            business_name: $('input[name="business_name"]').val().trim()
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 2});
    }

});