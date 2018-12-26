'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.AlmostDone = function () {

    return {
        init: function () {
            $('.resend-b2b-email-link').on('click', function (e) {
                e.preventDefault();
                $.ajax({
                    method: 'GET',
                    url: '/api/v1/businesses/resend-email-confirmation'
                });
            });
        }
    };
}();
