'use strict';

W.ns('W.users');

W.users.DetailPage = Class.extend({

    timezone: null,

    ui: {
        $userId: $('.user-id'),
        $messagesRegion: $('.messages'),
        $name: $('.info-form-wrapper input[name="name"]')
    },

    init: function () {
        var that = this;

        $('select').focus(function () {
            that.ui.$messagesRegion.text('');
        });

        if (that.ui.$name.val()) {
            that.ui.$name.prop('disabled', true);
        }

        this.changeAddress();
        this.preFillUserAddress();

        this.clickUpdateUserInfo();
        this.clickChangePassword();
        this.changeImage();
    },

    preFillUserAddress: function () {
        var that = this;
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/{0}/geo_locations'.format(that.ui.$userId.val()),
            success: function (data) {
                if (data && data.location) {
                    var l = data.location;
                    that.location = data.location;

                    if (l) {
                        $('input[name="address"]').val(W.common.Format.formatAddress(l)).trigger('change');
                    }
                }
            }
        });
    },

    changeAddress: function changeAddress() {
        var that = this,
            $googleInput = $('input[name="address"]'),
            GoogleLocations;

        if ($googleInput && $googleInput.length > 0) {
            GoogleLocations = new W.Common.GoogleLocations({$input: $googleInput.get(0)});

            GoogleLocations.initGoogleAutocomplete(
                function (autocomplete, $input) {
                    that.location = GoogleLocations.getAddressFromAutocomplete(autocomplete);

                    var $el = $($input);
                    $el.val(W.common.Format.formatAddress(that.location));
                    $el.blur();

                    that.updateTimezone(GoogleLocations);
                },
                function (results, status, $input) {
                    if (status === 'OK') {
                        that.location = GoogleLocations.getAddressFromPlace(results[0]);

                        var $el = $($input);
                        $el.val(W.common.Format.formatAddress(that.location));
                        $el.blur();

                        that.updateTimezone(GoogleLocations);
                    }
                },
                function ($input) {
                    var $removeBtn = $($input).parent().find('.remove-location');
                    $removeBtn.removeClass('hidden');
                    $removeBtn.on('click', function () {
                        that.location = {location_raw: {}};
                        $removeBtn.addClass('hidden');
                        $($input).val('');
                    });
                });
        }
    },

    updateTimezone: function updateTimezone(GoogleLocations) {
        var that = this;
        GoogleLocations.getTimezone(this.location.lat, this.location.lng, function (json) {
            that.timezone = json.timeZoneId;

            var $select = $('select[name="timezone"]');
            $select.find('option:selected').removeAttr('selected');
            $select.find('option[value="{0}"]'.format(that.timezone)).attr('selected', 'selected');
            $select.val(that.timezone);
        });
    },

    clickUpdateUserInfo: function clickUpdateUserInfo() {
        var that = this;
        $('.btn-update-user-info').on('click', function (e) {
            e.preventDefault();

            var data = collectUserData();
            if (isValid(data)) {
                $.ajax({
                    method: 'PUT',
                    url: '/api/v1/users/{0}/'.format(that.ui.$userId.val()),
                    dataType: 'json',
                    data: JSON.stringify(data),
                    success: function () {
                        that.showSuccessMessage('You profile information has been successfully updated');
                        var firstName = $('input[name="first_name"]').val(),
                            lastName = $('input[name="last_name"]').val();

                        $('.user-info .user-name').text('{0} {1}'.format(firstName, lastName));
                        $('.auth-menu .user-name').text(firstName);
                    },
                    error: function (error) {
                        that.showErrorMessage(error);
                    }
                });
            }

            function collectUserData() {
                var defaultSelectValue = '- Select One -',
                    birthMonth = $('select[name="birth_month"]').val(),
                    birthDay = $('select[name="birth_day"]').val(),
                    birthYear = $('select[name="birth_year"]').val(),
                    gender = $('select[name="gender"]').val(),
                    timezone = $('select[name="timezone"]').val();

                return {
                    'name': that.ui.$name.val(),
                    'first_name': $('input[name="first_name"]').val(),
                    'last_name': $('input[name="last_name"]').val(),
                    'email': $('input[name="email"]').val(),
                    'birth_month': birthMonth !== defaultSelectValue ? birthMonth : null,
                    'birth_day': birthDay !== defaultSelectValue ? birthDay : null,
                    'birth_year': birthYear !== defaultSelectValue ? birthYear : null,
                    'gender': gender !== defaultSelectValue ? gender : null,
                    'timezone': timezone !== defaultSelectValue ? timezone : that.timezone,
                    'location': that.location
                };
            }

            function isValid(data) {
                var birthDay = data.birth_day,
                    birthMonth = data.birth_month;

                if (birthDay && birthMonth && birthDay > 28 && birthMonth === 'feb') {
                    that.displayErrorMessage('February has only 28 days');
                    return false;
                }

                return true;
            }
        });
    },

    clickChangePassword: function clickChangePassword() {
        var that = this;

        $('.btn-update-pwd').on('click', function (e) {
            e.preventDefault();

            var data = {
                'curPwd': $('input[name="cur_pwd"]').val(),
                'pwd': $('input[name="pwd"]').val(),
                'pwd2': $('input[name="pwd2"]').val()
            };

            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/change-pwd'.format(that.ui.$userId.val()),
                dataType: 'json',
                data: JSON.stringify(data),
                success: function () {
                    that.showSuccessMessage('Your password has been changed')
                },
                error: function (error) {
                    that.showErrorMessage(error);
                }
            });
        });
    },

    showSuccessMessage: function showSuccessMessage(message) {
        var $messagesRegion = this.ui.$messagesRegion;
        $messagesRegion.text(message);
        $messagesRegion.removeClass('error-message');
        $messagesRegion.addClass('success-message');
        setTimeout(function () {
            $messagesRegion.text('');
        }, 3000);
    },

    showErrorMessage: function showErrorMessage(error) {
        var that = this,
            text = '';

        if (error.status === 400) {
            var errorText = JSON.parse(error.responseText);

            Object.keys(errorText).forEach(function(key) {
                text += key.replace('_', ' ') + ': ' + errorText[key]
            });

            that.displayErrorMessage(text);
        }
    },

    displayErrorMessage: function displayErrorMessage(message) {
        var $messagesRegion = this.ui.$messagesRegion;
        $messagesRegion.text(message);
        $messagesRegion.removeClass('success-message');
        $messagesRegion.addClass('error-message');
    },

    changeImage: function changeImage() {
        var that = this;

        $('.upload-image').on('change', function (e) {
            e.preventDefault();
            var $el = $(this),
                preview = $('.image'),
                file = $el[0].files[0],
                reader = new FileReader(),
                formData;

            reader.addEventListener('load', function () {
                preview[0].src = reader.result;
                preview.addClass('uploaded-image').removeClass('hidden');
                $('.default-image-label').removeClass('default-image-label').addClass('uploaded-image-label');
                $('.default-image').addClass('hidden');
            }, false);

            if (file) {
                reader.readAsDataURL(file);

                formData = new FormData();
                formData.append('file', file);
                formData.append('name', file.name);

                $.ajax({
                    type: 'POST',
                    url: '/api/v1/users/{0}/image'.format(that.ui.$userId.val()),
                    enctype: 'multipart/form-data',
                    data: formData,
                    processData: false,
                    contentType: false
                });
            }
        });
    }
});
