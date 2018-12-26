'use strict';

W.ns('W.common');

W.common.ActionRecorder = {

    track: function track(eventName, eventData) {
        if (window.mixpanel) {
            try {
                window.mixpanel.track(eventName, eventData);
            } catch (error) {
                console.error('Mixpanel: cannot log an event. Error message: [{0}].'.format(error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    },

    alias: function alias(user_id) {
        if (window.mixpanel) {
            try {
                window.mixpanel.alias(user_id);
            } catch (error) {
                console.error('Mixpanel: cannot alias the user {0}. Error message: [{1}].'.format(user_id, error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    },

    identify: function identify(user_id) {
        if (window.mixpanel) {
            try {
                window.mixpanel.identify(user_id);
            } catch (error) {
                console.error('Mixpanel: cannot identify the user {0}. Error message: [{1}].'.format(user_id, error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    },

    peopleSet: function peopleSet(json_data) {
        if (window.mixpanel) {
            try {
                window.mixpanel.people.set(json_data);
            } catch (error) {
                console.error('Mixpanel: cannot set people data. Error message: [{0}].'.format(error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    },

    timeEvent: function timeEvent(event_name) {
        if (window.mixpanel) {
            try {
                mixpanel.time_event(event_name);
            } catch (error) {
                console.error('Mixpanel: cannot start event time for [{0}]. Error message: [{1}].'.format(event_name, error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    }

};
