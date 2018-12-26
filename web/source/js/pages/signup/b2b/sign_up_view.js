'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpView = function () {

    var Model = W.common.Model,
        SignUpWizard = W.pages.b2b.SignUpWizard;

    return {
        init: function () {
            new SignUpWizard({
                model: new Model()
            });
        }
    };
}();
