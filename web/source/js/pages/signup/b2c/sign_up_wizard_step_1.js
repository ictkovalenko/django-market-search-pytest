'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizardStep1 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 1,
            model: options && options.model,
            submit_el: '.btn-b2c-step-1',
            template_el: '#b2c-wizard-1'
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({
            first_name: stepData && stepData.first_name,
            last_name: stepData && stepData.last_name
        });
    },

    validate: function validate() {
        var firstName = $('input[name="first_name"]').val(),
            lastName = $('input[name="last_name"]').val();

        if (!firstName || firstName.trim().length === 0) {
            $('.error-message').text('First name is required');
            return false;
        }

        if (!lastName || lastName.trim().length === 0) {
            $('.error-message').text('Last name is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {
            first_name: $('input[name="first_name"]').val().trim(),
            last_name: $('input[name="last_name"]').val().trim()
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 2});
    }

});
