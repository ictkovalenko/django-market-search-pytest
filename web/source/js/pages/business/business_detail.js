'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessDetail = Class.extend({

    ui: {
        $businessId: $('.business-id'),
        $locations: $('.location-select'),
        $locationOperationalHours: $('.location-operational-hours'),
        $btnUpdateInfo: $('.btn-update-info'),
        $hoursFieldGroup: $('.hours-field-group'),
        $dispensary: $('#dispensary'),
        $delivery: $('#delivery'),
        $grow_house: $('#grow_house'),
        $businessTypes: $('#dispensary, #delivery, #grow_house')
    },

    init: function init() {
        var that = this,
            currentLocationId = this.ui.$locations.val();

        this.retrieveLocation(currentLocationId, function (location) {
            if (location) {
                var HoursTemplate = _.template($('#operational-hours-field').html()),
                    phoneMask = W.common.Constants.masks.phone;

                that.ui.$locationOperationalHours.html(HoursTemplate({
                    days: W.common.Constants.days,
                    renderHours: _.template($('#operational-hours').html())
                }));

                $('input[name="phone"]').mask(phoneMask.mask, {placeholder: phoneMask.placeholder});

                that.preselectHours(location);
            }
        });

        this.clickUpdateBusinessInfo();
        this.changeLocation();
        this.changeBusinessType();
        // trigger checking if Operation Hours should be displayed
        this.ui.$businessTypes.trigger('change');

        var $input = $('input'),
            $selectTimezone = $('select[name="timezone"]'),
            $textarea = $('textarea');

        $input.on('focus', function () {
            $('.error-message').text('');
        });

        $input.on('change', function () {
            that.ui.$btnUpdateInfo.removeAttr('disabled');
        });

        $input.on('keyup', function () {
            that.ui.$btnUpdateInfo.removeAttr('disabled');
        });

        $textarea.on('focus', function () {
            $('.error-message').text('');
        });

        $textarea.on('change', function () {
            that.ui.$btnUpdateInfo.removeAttr('disabled');
        });

        $textarea.on('keyup', function () {
            that.ui.$btnUpdateInfo.removeAttr('disabled');
        });

        $selectTimezone.on('focus', function () {
            $('.error-message').text('');
        });

        $selectTimezone.on('change', function () {
            that.ui.$btnUpdateInfo.removeAttr('disabled');
        })
    },

    retrieveLocation: function retrieveLocation(locationId, successCallback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/locations/{1}'.format(this.ui.$businessId.val(), locationId),
            success: function (data) {
                successCallback(data.location);
            }
        });
    },

    preselectHours: function preselectHours(location) {
        var that = this;

        findAndSelect('mon_open', location);
        findAndSelect('mon_close', location);
        findAndSelect('tue_open', location);
        findAndSelect('tue_close', location);
        findAndSelect('wed_open', location);
        findAndSelect('wed_close', location);
        findAndSelect('thu_open', location);
        findAndSelect('thu_close', location);
        findAndSelect('fri_open', location);
        findAndSelect('fri_close', location);
        findAndSelect('sat_open', location);
        findAndSelect('sat_close', location);
        findAndSelect('sun_open', location);
        findAndSelect('sun_close', location);

        function findAndSelect(selectName, location) {
            var value = location[selectName],
                $select = $('select[name="{0}"]'.format(selectName));

            $select.find('option').removeProp('selected');
            $select.find('option[value="{0}"]'.format(value !== null ? value : '')).prop('selected', 'selected');

            $select.on('change', function () {
                that.ui.$btnUpdateInfo.removeAttr('disabled');
            });
        }
    },


    changeBusinessType: function () {
        var that = this;

        that.ui.$businessTypes.change(function () {
            if (that.ui.$grow_house && !that.ui.$delivery.is(':checked') && !that.ui.$dispensary.is(':checked')) {
                that.ui.$hoursFieldGroup.addClass('hidden');
            } else {
                that.ui.$hoursFieldGroup.removeClass('hidden');
            }
        });
    },

    clickUpdateBusinessInfo: function clickUpdateBusinessInfo() {
        var that = this;

        this.ui.$btnUpdateInfo.on('click', function (e) {
            e.preventDefault();
            var data = that.getValidatedData();
            if (data) {
                that.updateBusinessInfo(data);
            }
            return false;
        });
    },

    getOpenTime: function getOpenTime(day) {
        var val = $('select[name="{0}_open"]'.format(day)).val();
        return val !== '' ? val : null;
    },

    getCloseTime: function getCloseTime(day) {
        var val = $('select[name="{0}_close"]'.format(day)).val();
        return val !== '' ? val : null;
    },

    getValidatedData: function getValidatedData() {
        var that = this,
            $errorMessage = $('.error-message'),
            locationName = $('input[name="location_name"]').val(),
            manager = $('input[name="manager"]').val(),
            email = $('input[name="location_email"]').val(),
            phone = $('input[name="phone"]').val(),
            ext = $('input[name="ext"]').val(),
            dispensary = $('input[name="dispensary"]').is(':checked'),
            delivery = $('input[name="delivery"]').is(':checked'),
            growHouse = $('input[name="grow_house"]').is(':checked'),
            timezone = $('select[name="timezone"]').val(),
            about = $('textarea[name="about"]').val(),
            isOpenBeforeClose = function isOpenBeforeClose(open, close) {
                if (open && close) {
                    var o = new Date(Date.parse('1/1/1970 {0}'.format(open))),
                        c = new Date(Date.parse('1/1/1970 {0}'.format(close)));
                    return o < c;
                }
                return true;
            };

        if (!locationName || locationName.trim().length === 0) {
            $errorMessage.text('Business Name is required');
            return;
        }

        if (!email || email.trim().length === 0) {
            $errorMessage.text('Email is required');
            return;
        }

        if (!W.common.Constants.regex.email.test(email)) {
            $errorMessage.text('Invalid email address format');
            return;
        }

        if (!phone || phone.trim().length === 0) {
            $errorMessage.text('Phone Number is required');
            return;
        }

        if (ext && ext.length > 5) {
            $errorMessage.text('Extension can be 5 symbols max');
            return;
        }

        if (!dispensary && !delivery && !growHouse) {
            $errorMessage.text('Business Type is required');
            return;
        }

        if (!timezone || timezone === '- Select One -') {
            $errorMessage.text('Timezone is required');
            return;
        }

        var dayInvalid = false;
        $.each(W.common.Constants.days, function (index, day) {
            var openTime = that.getOpenTime(day.value),
                closeTime = that.getCloseTime(day.value);

            if (!isOpenBeforeClose(openTime, closeTime)) {
                $errorMessage.text('{0} close time cannot be earlier than open time'.format(day.name));
                dayInvalid = true;
            }

            if ((openTime && !closeTime) || (!openTime && closeTime)) {
                $errorMessage.text('{0} should have both open and close time selected.'.format(day.name));
                dayInvalid = true;
            }
        });

        if (dayInvalid) {
            return;
        }

        return {
            location_name: locationName.trim(),
            manager_name: manager ? manager.trim() : null,
            location_email: email.trim(),
            phone: phone.trim(),
            ext: ext ? ext.trim() : null,
            dispensary: dispensary,
            delivery: delivery,
            grow_house: growHouse,
            timezone: timezone,
            about: about,
            mon_open: this.getOpenTime('mon'), mon_close: this.getCloseTime('mon'),
            tue_open: this.getOpenTime('tue'), tue_close: this.getCloseTime('tue'),
            wed_open: this.getOpenTime('wed'), wed_close: this.getCloseTime('wed'),
            thu_open: this.getOpenTime('thu'), thu_close: this.getCloseTime('thu'),
            fri_open: this.getOpenTime('fri'), fri_close: this.getCloseTime('fri'),
            sat_open: this.getOpenTime('sat'), sat_close: this.getCloseTime('sat'),
            sun_open: this.getOpenTime('sun'), sun_close: this.getCloseTime('sun')
        }
    },

    updateBusinessInfo: function updateBusinessInfo(data) {
        var that = this,
            $errorMessage = $('.error-message');

        $.ajax({
            method: 'POST',
            url: '/api/v1/businesses/{0}/locations/{1}'.format(this.ui.$businessId.val(), that.ui.$locations.val()),
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                $errorMessage.text('Business Info was updated');
                $errorMessage.removeClass('error-message');
                $errorMessage.addClass('success-message');
                setTimeout(function () {
                    $errorMessage.text('');
                    $errorMessage.addClass('error-message');
                    $errorMessage.removeClass('success-message');
                }, 3000);
                // window.location.reload();
            },
            error: function (error) {
                if (error.status === 400) {
                    if (error.responseJSON) {
                        $.each(error.responseJSON, function (index, fieldErrors) {
                            $errorMessage.append(fieldErrors[0]);
                        });
                    } else {
                        $errorMessage.text(JSON.parse(error.responseText).error);
                    }
                }
            }
        });
    },

    changeLocation: function changeLocation() {
        var that = this;

        this.ui.$locations.on('change', function () {
            that.ui.$btnUpdateInfo.attr('disabled', 'disabled');
            var locationId = $(this).val();
            that.retrieveLocation(locationId, function (location) {
                if (location) {
                    $('input[name="location_name"]').val(location.location_name);
                    $('input[name="manager"]').val(location.manager_name);
                    $('input[name="location_email"]').val(location.location_email);
                    $('input[name="phone"]').val(location.phone);
                    $('input[name="ext"]').val(location.ext);
                    $('textarea[name="about"]').val(location.about);

                    if (location.dispensary) {
                        $('input[name="dispensary"]').prop('checked', true);
                    } else {
                        $('input[name="dispensary"]').removeProp('checked');
                    }

                    if (location.delivery) {
                        $('input[name="delivery"]').prop('checked', true);
                    } else {
                        $('input[name="delivery"]').removeProp('checked');
                    }

                    if (location.grow_house && !location.delivery && !location.dispensary) {
                        that.ui.$hoursFieldGroup.addClass('hidden');
                    } else {
                        that.ui.$hoursFieldGroup.removeClass('hidden');
                    }

                    var $select = $('select[name="timezone"]');
                    $select.find('option:selected').removeAttr('selected');
                    $select.find('option[value="{0}"]'.format(location.timezone)).attr('selected', 'selected');
                    $select.val(location.timezone ? location.timezone : '- Select One -');

                    that.preselectHours(location);
                }
            });
        });
    }

});
