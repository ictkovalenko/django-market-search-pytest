'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep6 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 6,
            model: options && options.model,
            submit_el: '.btn-b2b-step-6',
            template_el: '#b2b-wizard-6'
        });
    },

    renderHTML: function () {
        return this.$template({
            days: W.common.Constants.days,
            renderHours: _.template($('#operational-hours').html())
        });
    },

    validate: function validate() {
        var that = this,
            dayInvalid = false,
            isOpenBeforeClose = function isOpenBeforeClose(open, close) {
                if (open && close) {
                    var o = new Date(Date.parse('1/1/1970 {0}'.format(open))),
                        c = new Date(Date.parse('1/1/1970 {0}'.format(close)));
                    return o < c;
                }
                return true;
            };

        $.each(W.common.Constants.days, function (index, day) {
            var openTime = that.getOpenTime(day.value),
                closeTime = that.getCloseTime(day.value);

            if (!isOpenBeforeClose(openTime, closeTime)) {
                $('.error-message').text('{0} close time cannot be earlier than open time'.format(day.name));
                dayInvalid = true;
            }

            if ((openTime && !closeTime) || (!openTime && closeTime)) {
                $('.error-message').text('{0} should have both open and close time selected.'.format(day.name));
                dayInvalid = true;
            }
        });

        return !dayInvalid;
    },

    getOpenTime: function getOpenTime(day) {
        var val = $('select[name="{0}_open"]'.format(day)).val();
        return val !== '' ? val : null;
    },

    getCloseTime: function getCloseTime(day) {
        var val = $('select[name="{0}_close"]'.format(day)).val();
        return val !== '' ? val : null;
    },

    submit: function submit() {
        var data = {
            mon: {open: this.getOpenTime('mon'), close: this.getCloseTime('mon')},
            tue: {open: this.getOpenTime('tue'), close: this.getCloseTime('tue')},
            wed: {open: this.getOpenTime('wed'), close: this.getCloseTime('wed')},
            thu: {open: this.getOpenTime('thu'), close: this.getCloseTime('thu')},
            fri: {open: this.getOpenTime('fri'), close: this.getCloseTime('fri')},
            sat: {open: this.getOpenTime('sat'), close: this.getCloseTime('sat')},
            sun: {open: this.getOpenTime('sun'), close: this.getCloseTime('sun')}
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 7});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            var state = this.model.get(this.step);

            findAndSelect('mon_open', state.mon.open);
            findAndSelect('mon_close', state.mon.close);
            findAndSelect('tue_open', state.tue.open);
            findAndSelect('tue_close', state.tue.close);
            findAndSelect('wed_open', state.wed.open);
            findAndSelect('wed_close', state.wed.close);
            findAndSelect('thu_open', state.thu.open);
            findAndSelect('thu_close', state.thu.close);
            findAndSelect('fri_open', state.fri.open);
            findAndSelect('fri_close', state.fri.close);
            findAndSelect('sat_open', state.sat.open);
            findAndSelect('sat_close', state.sat.close);
            findAndSelect('sun_open', state.sun.open);
            findAndSelect('sun_close', state.sun.close);
        }

        function findAndSelect(selectName, hoursValue) {
            $('select[name="{0}"]'.format(selectName))
                .find('option[value="{0}"]'.format(hoursValue))
                .attr('selected', 'selected');
        }
    }

});