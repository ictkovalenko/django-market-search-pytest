'use strict';

W.ns('W.users');

W.users.ProfileForm = W.views.BaseView.extend({
    init: function init(cfg) {
        var cfg = cfg || {};
        this._super(cfg);
        this.formElem = (cfg.formElem === undefined) ? console.error('missing formElem') : $(cfg.formElem);
        this.submitButtonElem = (cfg.submitButtonElem === undefined) ? console.error('missing submitButtonElem') : cfg.submitButtonElem;
        this.user = (cfg.user === undefined) ? console.error('missing user') : cfg.user;

        this.configureFormValidation();
        this.configureEventHandlers();
    },
    configureEventHandlers: function configureEventHandlers() {
        var _this = this;

        this.elem.on('click', _this.submitButtonElem, function () {
            _this.submitLogin();
        });
    },
    configureFormValidation: function configureFormValidation() {
        var _this = this;
        _this.formElem.validate({
            rules: {
                name: {
                    required: true,
                    minlength: 1,
                    maxlength: 255
                }
            },
            messages: {
                name: {
                    required: 'You must enter a name',
                    minlength: 'Your name must be at least 1 characters long',
                    maxlength: 'Your name cannot be longer than 255 characters'
                }
            },
            errorPlacement: function (error, element) {
                // TODO handle validation errors
            }
        });
    },
    submitLogin: function submitLogin() {
        var name = this.formElem.find('[name=name]').val();

        // check via jquery validate
        if (!this.formElem.valid()) {
            return false;
        }

        $.ajax({
            url: '{0}/users/{1}/'.format(W.C.API_BASE, this.user.id),
            method: 'PUT',
            data: JSON.stringify({
                name: name
            })
        }).done(function (data) {
            window.location.reload;
        }).fail(function (res) {
            // TODO handle failures gracefully
        });
    }
});
