'use strict';

W.ns('W.common');

W.common.Wizard = Class.extend({

    regions: {
        $wizardContentRegion: $('.wizard-content-region')
    },

    init: function init(options) {
        this.model = options && options.model;

        this.initSteps();
        this.clickStep();
    },

    show: function show(wizardStep) {
        this.regions.$wizardContentRegion.html(wizardStep.renderHTML());
        wizardStep.initEventHandlers();
        this.cleanErrorMessagesOnFocus();
    },

    destroy: function destroy() {
        this.regions.$wizardContentRegion.html('');
    },

    initSteps: function initSteps() {
        throw new Error('Child class must implement initSteps.');
    },

    clickStep: function clickStep() {
        $('.wizard-step').on('click', function () {
            $.publish('show_step', {step: parseInt($(this).text(), 10)});
        });
    },

    handleStepClick: function handleStepClick(step) {
        var $selectedStep = $('.step-{0}'.format(step));

        if ($selectedStep.length === 0) {
            $('.wizard-step').addClass('finished').removeClass('active passed disabled');
        } else {
            $selectedStep.prevAll().addClass('passed').removeClass('active disabled');
            $selectedStep.addClass('active').removeClass('passed disabled');
            $selectedStep.nextAll().addClass('disabled').removeClass('active passed');
        }
    },

    cleanErrorMessagesOnFocus: function cleanErrorMessagesOnFocus() {
        $('input').on('focus', function () {
            $('.error-message').text('');
        });
    }

});