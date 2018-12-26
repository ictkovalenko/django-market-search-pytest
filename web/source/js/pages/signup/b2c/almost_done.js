'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.AlmostDone = function () {

    return {
        init: function () {
            var resend = $('.resend');

            var callApi = function(e) {
                resend.html('Sending email ...');

                e.preventDefault();
                $.ajax({
                    method: 'GET',
                    url: '/api/v1/users/resend-email-confirmation'
                }).success(function() {
                    resend.html('Email sent successfully.');
                }).fail(function() {
                    resend.html(
                        "There was a problem with sending your email.\n" +
                        '<a class="resend-email-link" href="#">Click here</a> to resend it.'
                    );
                    $('.resend-email-link').on('click', callApi);
                });
            };

            $('.resend-email-link').on('click', callApi);
        }
    };
}();
