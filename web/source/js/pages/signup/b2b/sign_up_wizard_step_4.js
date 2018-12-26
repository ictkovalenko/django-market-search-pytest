'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep4 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 4,
            model: options && options.model,
            submit_el: '.btn-b2b-step-4',
            template_el: '#b2b-wizard-4'
        });
    },

    renderHTML: function () {
        return this.$template({});
    },

    validate: function validate() {
        var isDispensary = $('input[name="dispensary"]').is(":checked"),
            isDelivery = $('input[name="delivery"]').is(":checked"),
            isGrowHouse = $('input[name="grow_house"]').is(":checked");

        if (!isDispensary && !isDelivery && !isGrowHouse) {
            $('.error-message').text('Business Type is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {
            dispensary: $('input[name="dispensary"]').is(":checked"),
            delivery: $('input[name="delivery"]').is(":checked"),
            growHouse: $('input[name="grow_house"]').is(":checked")
        };

        if (data.delivery) {
            data['delivery_radius'] = 10;
        }

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 5});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            var state = this.model.get(this.step);

            if (state.dispensary) {
                $('input[name="dispensary"]').prop('checked', 'checked');
            }

            if (state.delivery) {
                $('input[name="delivery"]').prop('checked', 'checked');
            }
        }
    }

});