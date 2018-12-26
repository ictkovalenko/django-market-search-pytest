'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep5 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 5,
            model: options && options.model,
            submit_el: '.btn-b2b-step-5',
            template_el: '#b2b-wizard-5'
        });

        this.stepData = {};
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({
            buildAddressDisplayName: this.buildAddressDisplayName,
            data: stepData,
            phone: stepData && stepData.phone
        });
    },

    buildAddressDisplayName: function buildAddressDisplayName(data) {
        var l = [];

        if (data) {
            if (data.street1) {
                l.push(data.street1);
            }

            if (data.city) {
                l.push(data.city);
            }

            if (data.state) {
                l.push(data.state);
            }

            if (data.zipcode) {
                l.push(data.zipcode);
            }
        }

        return l.join(', ');
    },

    initEventHandlers: function initEventHandlers() {
        this._super();

        var that = this,
            GoogleLocations = new W.Common.GoogleLocations({$input: $('input[name="address"]').get(0)}),
            phoneMask = W.common.Constants.masks.phone;

        $('input[name="phone"]').mask(phoneMask.mask, {placeholder: phoneMask.placeholder});

        GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input), a = GoogleLocations.getAddressFromAutocomplete(autocomplete);
                if (!a.street1 || !a.city || !a.state || !a.zipcode) {
                    $('.error-message').text('Address should have a street, city, state and zipcode');
                } else {
                    $el.val(W.common.Format.formatAddress(a));
                    $el.blur();
                    that.stepData = a;
                }
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var a = GoogleLocations.getAddressFromPlace(results[0]),
                        $el = $($input);

                    $el.val(W.common.Format.formatAddress(a));
                    $el.blur();

                    if (!a.street1 || !a.city || !a.state || !a.zipcode) {
                        $('.error-message').text('Address should have a street, city, state and zipcode');
                    } else {
                        that.stepData = a;
                    }
                }
            },
            function ($input) {
                var $removeBtn = $($input).parent().find('.remove-location');
                $removeBtn.removeClass('hidden');
                $removeBtn.on('click', function () {
                    $removeBtn.addClass('hidden');
                    $($input).val('');
                });
            });
    },

    validate: function validate() {
        var address = $('input[name="address"]').val(),
            phoneNumber = $('input[name="phone"]').val();

        function validateLength(value, fieldDisplayName) {
            if (!value || value.trim().length === 0) {
                $('.error-message').text('{0} is required'.format(fieldDisplayName));
                return false;
            }

            return true;
        }

        if (!validateLength(address, 'Address') || !validateLength(phoneNumber, 'Phone Number')) {
            return false;
        }

        if (!this.stepData.street1 || !this.stepData.city || !this.stepData.state || !this.stepData.zipcode) {
            $('.error-message').text('Address should have a street, city, state and zipcode');
            return false;
        }

        if (!W.common.Constants.regex.phone.test(phoneNumber)) {
            $('.error-message').text('Phone number must match the following format: 000-000-0000');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var that = this;

        this.stepData['phone'] = $('input[name="phone"]').val().trim();

        $.publish('update_step_data', {step: that.step, data: this.stepData});
        $.publish('show_step', {step: 6});
    }

});