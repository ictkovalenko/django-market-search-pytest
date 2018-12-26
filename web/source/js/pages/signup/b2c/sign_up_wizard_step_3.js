'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizardStep3 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 3,
            model: options && options.model,
            submit_el: '.btn-b2c-step-3',
            template_el: '#b2c-wizard-3'
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({email: stepData && stepData.email});
    },

    initEventHandlers: function initEventHandlers() {
        var that = this;

        $(this.submit_el).on('click', function (e) {
            e.preventDefault();
            if (that.validate()) {
                that.checkIfEmailRegistered($('input[name="email"]').val(),
                    function (data) {
                        if (!data || data.exist) {
                            $('.error-message').text('There is already an account associated with that email address');
                            return;
                        }

                        that.submit();
                    },
                    function () {
                        return false;
                    });
            }
        });
    },

    validate: function validate() {
        var email = $('input[name="email"]').val();

        if (!email || email.trim().length === 0) {
            $('.error-message').text('Email is required');
            return false;
        }

        if (!this.validateEmail(email)) {
            $('.error-message').text('Invalid email format');
            return false;
        }

        return true;
    },

    validateEmail: function validateEmail(email) {
        return W.common.Constants.regex.email.test(email);
    },

    checkIfEmailRegistered: function checkIfEmailRegistered(email, successCallback, errorCallback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/?email={0}'.format(encodeURIComponent(email)),
            dataType: 'json',
            success: function (data) {
                successCallback(data);
            },
            error: function (error) {
                errorCallback(error);
            }
        });
    },

    submit: function submit() {
        var data = {email: $('input[name="email"]').val().trim()};
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 4});
    }

});
