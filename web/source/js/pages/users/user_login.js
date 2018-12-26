'use strict';

W.ns('W.pages');

W.pages.UserLogin = W.views.BaseView.extend({

    ui: {
        $btnLoginSubmit: $('.send-login'),
        $btnSendPwdResetSubmit: $('.btn-send-password-reset'),
        $btnPwdResetSubmit: $('.btn-password-reset'),
        $messageRegion: $('.error-message')
    },

    init: function init() {
        var that = this;
        $('input').on('focus', function () {
            that.ui.$messageRegion.text('')
        });

        this.validateTokenIfPresent();

        this.clickLoginSubmit();
        this.clickSendPwdResetSubmit();
        this.clickPwdResetSubmit();
    },

    validateTokenIfPresent: function validateTokenIfPresent() {
        var qs = W.qs(),
            token = qs['t'],
            userId = qs['uid'];

        if (userId && token) {
            $.ajax({
                method: 'GET',
                url: '/api/v1/users/reset-password?uid={0}&t={1}'.format(userId, token),
                success: function () {
                    $('.forgot-message').html('<span>Create your new password</span>');
                    $('.password-reset').removeClass('hidden');
                },
                error: function (error) {
                    if (error.status === 400) {
                        $('.forgot-message').text(JSON.parse(error.responseText).error);
                        $('.password-reset').html('');
                    }
                }
            });
        }
    },

    clickLoginSubmit: function clickLoginSubmit() {
        var that = this;
        this.ui.$btnLoginSubmit.on('click', function (e) {
            e.preventDefault();
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/login',
                dataType: 'json',
                data: JSON.stringify({email: $('#login').val(), password: $('#password').val()}),
                success: function (data) {
                    var user = data.user;
                    if (user) {
                        W.common.ActionRecorder.identify(user.id);
                        W.common.ActionRecorder.peopleSet({
                            '$first_name': user.first_name,
                            '$last_name': user.last_name,
                            '$last_login': new Date(),
                            '$email': user.email,
                            'account_type': user.type
                        });
                    }
                    var url = new URL(document.location);
                    var next = url.searchParams.get('next');

                    if (next) {
                        window.location.href = next;
                    } else {
                        window.location.href = '/';
                    }
                },
                error: function (error) {
                    if (error.status === 400) {
                        that.ui.$messageRegion.text(JSON.parse(error.responseText).error);
                    }
                }
            });
        });
    },

    clickSendPwdResetSubmit: function clickPwdResetSubmit() {
        var that = this;
        this.ui.$btnSendPwdResetSubmit.on('click', function (e) {
            e.preventDefault();
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/reset-password',
                dataType: 'json',
                data: JSON.stringify({action: 'send-reset-email', email: $('#login').val()}),
                success: function () {
                    window.location.href = '/accounts/password/reset/done';
                },
                error: function (error) {
                    if (error.status === 400) {
                        that.ui.$messageRegion.text(JSON.parse(error.responseText).error);
                    }
                }
            });
        });
    },

    clickPwdResetSubmit: function clickPwdResetSubmit() {
        var that = this;
        this.ui.$btnPwdResetSubmit.on('click', function (e) {
            e.preventDefault();
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/reset-password',
                dataType: 'json',
                data: JSON.stringify({
                    action: 'reset-pwd',
                    uid: $('.uid').val(),
                    t: $('.t').val(),
                    pwd: $('#pwd').val(),
                    pwd2: $('#pwd2').val()
                }),
                success: function () {
                    window.location.href = '/accounts/password/reset/done?done=all_right';
                },
                error: function (error) {
                    if (error.status === 400) {
                        that.ui.$messageRegion.text(JSON.parse(error.responseText).error);
                    }
                }
            });
        });
    }

});
