'use strict';

W.ns('W.common');

W.common.Dialog = function ($el, closeCallback, options) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: (options && options.height) || 450,
            width: (options && options.width) || 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", (options && options.maxWidth) || "500px");
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};

W.common.VerifyEmailDialog = function () {
    W.common.Dialog($('.verify-email-dialog'), function () {
        $('.btn-yes').off('click');
        $('.dialog-verify-email-link').off('click');
    }, {height: 250, width: 380});

    $('.dialog-verify-email-link').on('click', function (e) {
        e.preventDefault();
        $.ajax({method: 'GET', url: '/api/v1/users/resend-email-confirmation'});
    });

    $('.btn-yes').on('click', function (e) {
        e.preventDefault();
        $('.verify-email-dialog').dialog('close');
    });
};

W.common.ConfirmDialog = function ($el, closeCallback, options) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            minHeight: 'auto',
            height: (options && options.height) || 200,
            width: (options && options.width) || 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("max-width", "500px");
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};

W.common.RateDialog = function ($el, closeCallback) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 400,
            width: 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", "450px");

                var $rateStarsRegion = $('.rate-stars');
                if ($rateStarsRegion) {
                    $rateStarsRegion.rateYo({
                        spacing: '10px',
                        starWidth: '50px',
                        maxValue: 5,
                        precision: 1,
                        halfStar: true,
                        normalFill: '#f4f4f4', // $white-smoke
                        ratedFill: '#6bc331', // $avocado-green
                        onSet: function () {
                            var $errorMessageRegion = $('.error-message');
                            if ($errorMessageRegion) {
                                $errorMessageRegion.text('');
                            }
                        }
                    });
                }
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};

W.common.ReviewDialog = function ($el, closeCallback, options) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            classes: {
                'ui-dialog': 'srx-dialog'
            },
            closeOnEscape: true,
            height: (options && options.height) || 'auto',
            width: (options && options.width) || 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css('max-width', (options && options.maxWidth) || '450px');
                $(this).css('min-height', (options && options.minHeight) || 'auto');
                $('.srx-dialog').css('min-height', (options && options.minHeight) || 'auto');
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};


W.common.EligibleDialog = function (options) {
    if (options.userId) {
        return;
    }

    var settings = new W.users.UserSettings({ userId: options.userId });

    settings.get(settings.settingName_Eligible, function(eligible) {
        if (eligible) {
            return;
        }

        if (/bot|google|baidu|bing|msn|duckduckbot|teoma|slurp|yandex|crawler|spider|robot|crawling/i
          .test(navigator.userAgent)) {
            return;
        }

        var $dialog = $('#eligible-dialog'),
            $backdrop = $('.dialog-backdrop'),
            $checkbox = $dialog.find('input'),
            $button = $dialog.find('button');

        $dialog.css('display', 'initial');
        $backdrop.css('display', 'initial');
        $checkbox.prop('checked', false);
        $button.prop('disabled', true);

        $checkbox.change(function() {
            $button.prop('disabled', !$checkbox.is(":checked"));
        });

        $button.on('click', function() {
            settings.update(settings.settingName_Eligible, true);
            $dialog.css('display', 'none');
            $backdrop.css('display', 'none');
        });
    });




};