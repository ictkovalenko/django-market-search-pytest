'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep7 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 7,
            model: options && options.model,
            submit_el: '.btn-b2b-step-7',
            template_el: '#b2b-wizard-7'
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();

        var that = this;
        $('.btn-b2b-skip-7').on('click', function (e) {
            e.preventDefault();
            $.publish('update_step_data', {step: that.step, data: {skipped: true}});
            $.publish('show_step', {step: 8});
        });

        $('.upload-image').on('change', function (e) {
            e.preventDefault();
            var preview = $('.uploaded-img'),
                file = $(this)[0].files[0],
                reader = new FileReader();

            reader.addEventListener("load", function () {
                preview[0].src = reader.result;
                preview.removeClass('hidden');
                $('.fa-camera').addClass('hidden');
            }, false);

            if (file) {
                reader.readAsDataURL(file);
            }
        });
    },

    renderHTML: function () {
        return this.$template({});
    },

    validate: function validate() {
        var file = $('.upload-image')[0].files[0];
        if (!file) {
            $('.error-message').text('Image file is required');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var file = $('.upload-image')[0].files[0],
            formData = new FormData();

        formData.append('file', file);
        formData.append('name', file.name);

        $.publish('update_step_data', {step: this.step, data: formData});
        $.publish('show_step', {step: 8});
    }

});