'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpWizard = W.common.Wizard.extend({

    steps: {},

    init: function init(options) {
        this._super({
            model: options && options.model
        });

        this.name = 'SignUpWizard';
        this.showStep({step: 1});

        W.subscribe.apply(this);
    },

    _on_show_step: function _on_show_step(ev, data) {
        this.showStep({step: data.step});
        this.handleStepClick(data.step);
    },

    _on_update_step_data: function _on_update_step_data(ev, data) {
        this.updateData(data);
    },

    _on_submit_form: function _on_submit_form(ev, data) {
        var userGeoLocation = Cookies.get('user_geo_location');
        userGeoLocation = userGeoLocation ? JSON.parse(userGeoLocation) : {};

        $.ajax({
            method: 'POST',
            url: '/api/v1/users/signup',
            dataType: 'json',
            data: JSON.stringify({
                first_name: data[1].first_name, last_name: data[1].last_name,
                is_age_verified: data[2].is_age_verified,
                email: data[3].email,
                pwd: data[4].pwd, pwd2: data[4].pwd2,
                is_terms_accepted: data[5].terms,
                location: {
                    street1: userGeoLocation.street1 || '',
                    city: userGeoLocation.city || '',
                    state: userGeoLocation.state || '',
                    zipcode: userGeoLocation.zipcode || '',
                    lat: userGeoLocation.lat || null,
                    lng: userGeoLocation.lng || null,
                    location_raw: {}
                }
            }),
            success: function (data) {
                W.common.ActionRecorder.alias(data.user.id);
                window.location.href = '/users/signup/done';
            },
            error: function (error) {
                if (error.status === 400) {
                    $('.error-message').text(JSON.parse(error.responseText).error);
                }
            }
        });
    },

    initSteps: function initSteps() {
        this.steps[1] = new W.pages.b2c.SignUpWizardStep1({model: this.model});
        this.steps[2] = new W.pages.b2c.SignUpWizardStep2({model: this.model});
        this.steps[3] = new W.pages.b2c.SignUpWizardStep3({model: this.model});
        this.steps[4] = new W.pages.b2c.SignUpWizardStep4({model: this.model});
        this.steps[5] = new W.pages.b2c.SignUpWizardStep5({model: this.model});
    },

    showStep: function showStep(data) {
        this.destroy();
        this.show(this.steps[data.step]);
    },

    updateData: function updateData(data) {
        this.model.set(data.step, data.data);
    }

});
