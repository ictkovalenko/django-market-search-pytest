'use strict';

W.ns('W.users');


W.users.UserSettings = Class.extend({
    init: function init(options) {
        this.userId = options.userId;
        if (options.userId) {
            this.engine = W.users.UserSettingsRemote;
        } else {
            this.engine = W.users.UserSettingsLocal;
        }

        this.settingName_SearchFilter = 'search_results_filter';
        this.settingName_WizardSearch = 'search_vt_wizard';
        this.settingName_Eligible = 'eligible';

    },

    get: function get(settingName, successCallback, errorCallback) {
        function wrappedCallback(data) {
            var settingValue;
            if (data) {
                var setting = _.find(data, function(e) { return e.setting_name === settingName; });
                if (setting) {
                    settingValue = setting.setting_value;
                }
            } else {
                settingValue = successCallback();
            }
            successCallback(settingValue);
        }

        this.engine.getAll(this.userId, wrappedCallback, errorCallback);
    },

    update: function update(settingName, settingValue, successCallback, errorCallback) {
        this.engine.update(this.userId, settingName, settingValue, successCallback, errorCallback);
    },

    remove: function remove(settingName, successCallback, errorCallback) {
        this.engine.remove(this.userId, settingName, successCallback, errorCallback);
    }

});


W.users.UserSettingsLocal = function () {

    return {
        settingsCookie: 'user_settings',

        getAll: function getAll(userId, successCallback, errorCallback) {
            var settings = Cookies.get(this.settingsCookie);
            if (settings) {
                settings = JSON.parse(settings);
            }
            successCallback(settings);
        },

        update: function update(userId, settingName, settingValue, successCallback, errorCallback) {
            var settingsCookie = this.settingsCookie;

            function wrappedCallback(settings) {
                settings = settings || [];

                var setting = _.find(settings, function(e) { return e.setting_name === settingName; });
                if (setting) {
                    setting.setting_value = settingValue;
                } else {
                    settings.push({
                        setting_name: settingName,
                        setting_value: settingValue
                    });
                }

                Cookies.set(settingsCookie, JSON.stringify(settings));

                if (successCallback) {
                    successCallback();
                }

            }

            this.getAll(userId, wrappedCallback);
        },

        remove: function(userId, settingName, successCallback, errorCallback) {
            var settingsCookie = this.settingsCookie;

            function wrappedCallback(settings) {
                settings = settings || [];

                settings = _.filter(settings, function(elem) {
                    return elem.setting_name !== settingName;
                });

                Cookies.set(settingsCookie, JSON.stringify(settings));

                if (successCallback) {
                    successCallback();
                }
            }

            this.getAll(userId, wrappedCallback);
        }
    };

}();


W.users.UserSettingsRemote = function () {

    return {

        getAll: function getAll(userId, successCallback, errorCallback) {
            $.ajax({
                method: 'GET',
                url: '/api/v1/users/{0}/settings'.format(userId),
                success: successCallback,
                error: function (error) {
                    console.log('Cannot get a settings for user: {1}'.format(error.responseText));

                    if (errorCallback) {
                        errorCallback(error);
                    }
                }
            });
        },

        update: function update(userId, settingName, settingValue, successCallback, errorCallback) {
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/settings'.format(userId),
                dataType: 'json',
                data: JSON.stringify({
                    setting_name: settingName,
                    setting_value: settingValue
                }),
                success: function () {
                    if (successCallback) {
                        successCallback();
                    }
                },
                error: function (error) {
                    console.log('Cannot update a setting {0} for user: {1}'.format(settingName));

                    if (errorCallback) {
                        errorCallback(error);
                    }
                }
            });
        }
    };

}();
