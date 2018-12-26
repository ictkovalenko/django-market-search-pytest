'use strict';

W.ns('W.common');

W.common.WizardStep = Class.extend({

    init: function init(cfg) {
        var config = cfg || {};

        this.step = (config.step === undefined) ? console.error('step missing') : config.step;
        this.model = config.model || new W.common.Model();

        // JQuery selector for submit elem
        this.submit_el = (config.submit_el === undefined) ?
            console.error('submit missing') :
            config.submit_el;

        // Underscore template
        this.$template = (config.template_el === undefined) ?
            console.error('template missing') :
            _.template($(config.template_el).html());
    },

    initEventHandlers: function initEventHandlers() {
        var that = this;

        $(this.submit_el).on('click', function (e) {
            e.preventDefault();
            if (that.validate()) {
                that.submit();
            }
        });
    },

    renderHTML: function renderHTML() {
        throw new Error('Child class must implement renderHTML.');
    },

    validate: function validate() {
        throw new Error('Child class must implement validate.');
    },

    submit: function submit() {
        throw new Error('Child class must implement submit.');
    }

});