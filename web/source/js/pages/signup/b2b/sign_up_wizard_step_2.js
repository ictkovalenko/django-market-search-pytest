'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep2 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 2,
            model: options && options.model,
            submit_el: '.btn-b2b-step-2',
            template_el: '#b2b-wizard-2'
        });
    },

    initEventHandlers: function initEventHandlers() {
        var that = this;

        $(this.submit_el).on('click', function (e) {
            e.preventDefault();
            if (that.validate()) {
                that.checkIfEmailRegistered($('input[name="user_email"]').val(),
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

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({user_email: stepData && stepData.user_email});
    },

    validate: function validate() {
        var userEmail = $('input[name="user_email"]').val();

        if (!userEmail || userEmail.trim().length === 0) {
            $('.error-message').text('Email address is required');
            return false;
        }

        if (!this.validateEmail(userEmail)) {
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
        var data = {
            user_email: $('input[name="user_email"]').val().trim()
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 3});
    }

});