'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizardStep4 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 4,
            model: options && options.model,
            submit_el: '.btn-b2c-step-4',
            template_el: '#b2c-wizard-4'
        });
    },

    renderHTML: function () {
        return this.$template();
    },

    validate: function validate() {
        var pwd = $('input[name="pwd"]').val(),
            pwd2 = $('input[name="pwd2"]').val();

        if (!pwd || pwd.trim().length === 0) {
            $('.error-message').text('Password is required');
            return false;
        }

        if (pwd.trim().length < 6) {
            $('.error-message').text('Password should be at least 6 characters');
            return false;
        }

        if (!this.containsSpecialChar(pwd)) {
            $('.error-message').text('Password should contain at least 1 special character');
            return false;
        }

        if (!pwd2 || pwd2.trim().length === 0) {
            $('.error-message').text('Password confirmation is required');
            return false;
        }

        if (pwd !== pwd2) {
            $('.error-message').text('Passwords don\'t match');
            return false;
        }

        return true;
    },

    containsSpecialChar: function containsSpecialChar(pwd) {
        return W.common.Constants.regex.specialChar.test(pwd);
    },

    submit: function submit() {
        var data = {
            pwd: $('input[name="pwd"]').val().trim(),
            pwd2: $('input[name="pwd2"]').val().trim()
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 5});
    }

});
