/*
 *   Put global methods here that are shared across all pages
 */
'use strict';

/*! Tiny Pub/Sub - v0.7.0 - 2013-01-29
 * https://github.com/cowboy/jquery-tiny-pubsub
 * Copyright (c) 2013 "Cowboy" Ben Alman; Licensed MIT */
(function ($) {

    var o = $({});

    $.subscribe = function () {
        o.on.apply(o, arguments);
    };

    $.unsubscribe = function () {
        o.off.apply(o, arguments);
    };

    $.publish = function () {
        o.trigger.apply(o, arguments);
    };

}(jQuery));

/*
 *   Python-esque string formatting for JS
 *   Usage:
 *   '{0}bar {1}'.format('foo', 'baz') // 'foobar baz'
 *   'My name is {name}'.format({name: 'Justin'}) // 'My name is Justin'
 */

String.prototype.format = function () {
    var args = arguments;

    if (Object.prototype.toString.call(arguments[0]).match(/^\[object (.*)\]$/)[1] === 'Object') {
        return this.replace(/{(\w+)}/g, function (match, memberName) {
            if (typeof args[0][memberName] === undefined) {
                console.warn(memberName + ' not found in the parameter list');
            }

            return typeof args[0][memberName] !== undefined ? args[0][memberName] : match;
        });
    } else {
        return this.replace(/{(\d+)}/g, function (match, number) {
            if (typeof args[number] === undefined) {
                console.warn(number + ' not found in the parameter list');
            }
            return typeof args[number] !== undefined ? args[number] : match;
        });
    }
};


var W = {
    ns: function ns(namespace) {
        // generate namespaces to help us organize our code in the global scope
        var nsparts = namespace.split('.');
        var parent = W;

        if (nsparts[0] === 'W') {
            nsparts = nsparts.slice(1);
        }

        for (var i = 0; i < nsparts.length; i++) {
            var partname = nsparts[i];
            if (typeof parent[partname] === 'undefined') {
                parent[partname] = {};
            }
            parent = parent[partname];
        }

        return parent;
    },
    C: { // global constants
        API_BASE: '/api/v1',
        CHROME: 'CHROME',
        SAFARI: 'SAFARI',
        IE: 'IE',
        FF: 'FF',
        OTHER: 'OTHER'
    },
    getCookie: function getCookie(name) {
        // based on https://github.com/HenrikJoreteg/cookie-getter
        var cookie = document.cookie,
            setPos = cookie.search(new RegExp('\\b' + name + '=')),
            stopPos = cookie.indexOf(';', setPos),
            res;

        if (!~setPos) {
            return null;
        }

        res = decodeURIComponent(cookie.substring(setPos, ~stopPos ? stopPos : undefined).split('=')[1]);

        return (res.charAt(0) === '{') ? JSON.parse(res) : res;
    },
    isLoading: function isLoading() {
        // is an ajax request in progress?
        return AJAX_COUNT !== 0;
    },
    ellipser: function ellipser(cfg) {
        /*
         Shortens strings to specified length and adds '...'
         */
        cfg = cfg || {};
        var str = (cfg.str === undefined || cfg.str === null) ? '' : cfg.str;
        var max = (cfg.max === undefined) ? 10 : cfg.max;

        if (str.length > max) {
            return '{0}...'.format(str.substr(0, max));
        } else {
            return str;
        }
    },
    subscribe: function subscribe() {
        /*
         *   Subscribe to events for non-ES6 modules
         */
        var event;
        var eventPrefix = '_on_';

        if (this.name === undefined) {
            alert('Error in common.subscribeModule() : name must exist on implementing module');
            return;
        }

        for (var prop in this) {
            if (prop.substring(0, 4) === eventPrefix) {
                event = prop.replace(eventPrefix, '');
                $.subscribe('{event}.{name}'.format({event: event, name: this.name}), $.proxy(this[prop], this));
            }
        }
    },
    qs: function qs(queryString) {
        /*
         Takes in query string and returns a dictionary of any params found
         :qs is optional - will use current URL if not supplied
         */
        var query = (queryString === undefined) ? window.location.search.substring(1) : queryString.split('?')[1],
            vars = query.split('&'),
            data = {};

        for (var i = 0, len = vars.length; i < len; i++) {
            var pair = vars[i].split('=');
            data[pair[0]] = pair[1];
        }

        return data;
    },
    track: function(event_data){
        $.ajax({
            method: 'POST',
            data:  JSON.stringify(event_data),
            url: '/api/v1/analytics/track',
            success: function (data) {
                console.log(data);
            }
        });        
    },
    detectBrowser: function detectBrowser() {
        var safari = /.*?(Safari)/i,
            chrome = /.*?(Chrome)/i,
            firefox = /.*?(Firefox)/i,
            ie = /.*?(Trident)/i,
            opera = /.*?(Opera)/i,
            safariVer = /Version\S(\d+).(\d+).(\d+)/i,
            firefoxVer = /Firefox\S(\d+).(\d+)/i,
            chromeVer = /Chrome\S(\d+).(\d+).(\d+).(\d+)/i,
            operaVer = /Version\S(\d+).(\d+)/i,
            ieVer = /rv:(\d+).(\d+)/i,
            browserInfo = {
                type: '',
                version: ''

            },
            userAgent = window.navigator.userAgent;

        try {

            // detect browser type and version
            if (chrome.test(userAgent)) {
                // chrome
                browserInfo.type = W.C.CHROME;
                browserInfo.version = (userAgent.match(chromeVer) === null) ? W.C.OTHER : userAgent.match(chromeVer)[0].split('/')[1];
            } else if (safari.test(userAgent) && !chrome.test(userAgent)) {
                // safari
                browserInfo.type = W.C.SAFARI;
                browserInfo.version = (userAgent.match(safariVer) === null) ? W.C.OTHER : userAgent.match(safariVer)[0].split('/')[1];
            } else if (firefox.test(userAgent)) {
                // firefox
                browserInfo.type = W.C.FF;
                browserInfo.version = (userAgent.match(firefoxVer) === null) ? W.C.OTHER : userAgent.match(firefoxVer)[0].split('/')[1];
            } else if (ie.test(userAgent)) {
                // ie
                browserInfo.type = W.C.IE;
                browserInfo.version = (userAgent.match(ieVer) === null) ? W.C.OTHER : parseInt(userAgent.match(ieVer)[0].split(':')[1]);
            } else if (opera.test(userAgent)) {
                // opera
                browserInfo.type = W.C.OPR;
                browserInfo.version = (userAgent.match(operaVer) === null) ? W.C.OTHER : userAgent.match(operaVer)[0].split('/')[1];
            } else {
                // other
                browserInfo.type = W.C.OTHER;
                browserInfo.version = W.C.OTHER;
            }
        } catch (e) {
            console.error('Error detecting browser');
        }

        return browserInfo;
    }


};

W.ns('W.pages');

W.pages.Common = {
    ajaxSetup: function ajaxSetup() {
        $.ajaxSetup({
            // set csrf token globally so we never have to worry about it
            headers: {
                'X-CSRFToken': W.getCookie('csrftoken'),
                'Authorization': 'Basic ' + btoa(HTTP_USERNAME + ":" + HTTP_PASSWORD)
            },
            // do not cache requests
            cache: false,
            dataType: 'json',
            contentType: 'application/json' //; charset=utf-8'
        });
    }
};


/*
 Global AJAX setup
 This must exist outside of document.ready to catch all ajax calls
 Count ajax requests and display loading spinner if any are active and take longer than timeout time to return
 */
var AJAX_COUNT = 0;
var AJAX_TIMEOUT = undefined;

W.pages.Common.ajaxSetup();

$(document).on('ajaxSend', function () {
    AJAX_COUNT += 1;

    // don't show loading until after some time passes to prevent quick flashes of spinner
    if (AJAX_TIMEOUT) {
        clearTimeout(AJAX_TIMEOUT);
    }

    AJAX_TIMEOUT = setTimeout(function () {
        if (W.isLoading()) {
            $('#loading-spinner').show();
        } else {
            $('#loading-spinner').hide();
        }
    }, 500);
});

$(document).on('ajaxComplete', function () {
    AJAX_COUNT -= 1;
    if (AJAX_COUNT === 0) {
        $('#loading-spinner').hide();
    }
});

$(document).on('click', function (e) {
    var elem = $(e.target);
    if (!(elem.parents('.popup-container').length || elem.hasClass('.popup-container'))) {
        $.publish('close_popup');
    }
});
