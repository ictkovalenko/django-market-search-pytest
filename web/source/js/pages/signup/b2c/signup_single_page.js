'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpSinglePage = Class.extend({

    ui: {
        $name: $('#id_name'),
        $email: $('#id_email'),
        $firstName: $('#id_first_name'),
        $lastName: $('#id_last_name'),
        $pwd: $('#id_pwd'),
        $pwd2: $('#id_pwd2'),
        $isTermsAccepted: $('#id_is_terms_accepted'),
        $isAgeVerified: $('#id_is_age_verified'),
        $button: $('.form button')
    },

    init: function init() {
        this.ui.$isTermsAccepted.prop('checked', false);
        this.ui.$isAgeVerified.prop('checked', false);
        this.ui.$button.prop('disabled', true);
        this.ui.$button.on('click', this.submit.bind(this));

        $(document).on('keyup', this.setButtonState.bind(this));
        $(document).on('click', this.setButtonState.bind(this));
    },

    getInputs: function() {
        return {
            name: this.ui.$name.val(),
            email: this.ui.$email.val(),
            first_name: this.ui.$firstName.val(),
            last_name: this.ui.$lastName.val(),
            is_age_verified: this.ui.$isAgeVerified.prop('checked'),
            is_terms_accepted: this.ui.$isTermsAccepted.prop('checked'),
            pwd: this.ui.$pwd.val(),
            pwd2: this.ui.$pwd2.val()
        }
    },

    areInputsValid: function(inputs) {
        return _.every(inputs);
    },

    setButtonState: function() {
        var canSubmit = this.areInputsValid(this.getInputs());
        this.ui.$button.prop('disabled', !canSubmit);
    },

    submit: function() {
        var payload = this.getInputs();
        var userGeoLocation = Cookies.get('user_geo_location');
        var settings = new W.users.UserSettings({ userId: null });
        settings.get(settings.settingName_WizardSearch, function (data) {
            if (typeof data === 'object') {
                payload.search_criteria = {
                    step1: data['1'], step2: data['2'],
                    step3: data['3'], step4: data['4']
                }
            }
        });

        userGeoLocation = userGeoLocation ? JSON.parse(userGeoLocation) : {};

        payload.location = {
            street1: userGeoLocation.street1 || '',
            city: userGeoLocation.city || '',
            state: userGeoLocation.state || '',
            zipcode: userGeoLocation.zipcode || '',
            lat: userGeoLocation.lat || null,
            lng: userGeoLocation.lng || null,
            location_raw: {}
        };

        $.ajax({
            method: 'POST',
            url: '/api/v1/users/signup',
            dataType: 'json',
            data: JSON.stringify(payload),
            success: function (data) {
                W.common.ActionRecorder.alias(data.user.id);
                window.location.href = '/users/signup/done';
            },
            error: function (response) {
                var errors = JSON.parse(response.responseText).error;
                $('.error_icon').css('display', 'none');

                _.mapKeys(errors, function(v, k) {
                    $('#error_' + k).text(v[0]);
                    $('#error_icon_' + k).css('display', 'initial');
                });
            }
        });
    }

});