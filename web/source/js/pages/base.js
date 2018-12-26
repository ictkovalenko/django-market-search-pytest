/*
 *   JS to support base.html
 */
'use strict';

W.ns('W');

W.Base = function () {

    var BaseView = W.views.BaseView;

    return {
        init: function init() {
            new BaseView();
        }
    };
}();
