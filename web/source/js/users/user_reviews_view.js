'use strict';

W.ns('W.users');

W.users.ReviewsView = function () {

    var ReviewsPage = W.users.ReviewsPage;

    return {
        init: function () {
            new ReviewsPage();
        }
    };
}();
