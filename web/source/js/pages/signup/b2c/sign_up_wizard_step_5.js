'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizardStep5 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 5,
            model: options && options.model,
            submit_el: '.btn-b2c-step-5',
            template_el: '#b2c-wizard-5'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        $('.check').on('click', function () {
            $('.error-message').text('');
        });

        $('.terms-link').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.terms-dialog'));
        });

        $('.policy-link').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.privacy-dialog'));
        });
    },

    renderHTML: function () {
        return this.$template();
    },

    validate: function validate() {
        var isTermsChecked = $('input[name="terms"]').is(':checked');

        if (!isTermsChecked) {
            $('.error-message').text('Agreement is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {terms: $('input[name="terms"]').is(":checked")};
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('submit_form', this.model.getData());
    }

});
