'use strict';

W.ns('W.users');

W.users.Login = function () {

    var UserLogin = W.pages.UserLogin;

    return {
        init: function init() {
            new UserLogin();
        }
    };
}();
