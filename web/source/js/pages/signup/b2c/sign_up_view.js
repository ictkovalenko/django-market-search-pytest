'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.SignUpView = function () {

    var Model = W.common.Model,
        SignUpWizard = W.pages.b2c.SignUpWizard;

    return {
        init: function () {
            new SignUpWizard({
                model: new Model()
            });
        }
    };
}();
