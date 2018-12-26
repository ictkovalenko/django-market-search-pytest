'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    ui: {
        $userLocationBtn: $('.your-location')
    },

    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;

        this.initVtLookupField();
        this.updateLocation();
    },

    initVtLookupField: function initVtLookupField() {
        var lookupTemplate = _.template($('#vt-lookup-field').html());
        $('.vt-name-field').html(lookupTemplate({
            'lookup_placeholder': 'Blue Dream, Maui Wowie, Pineapple express ...'
        }));
        new W.pages.vt.VtLookup({ onSelect: this.navigateToVtDetailPage });
    },

    navigateToVtDetailPage: function navigateToVtDetailPage(selected) {
        if (selected.variety && selected.slug) {
            window.location.href = '/vts/{0}/{1}/'.format(selected.variety, selected.slug);
        }
    },

    updateLocation: function updateLocation() {
        this.ui.$userLocationBtn.on('click', function () {
            W.Location.init({
                location: null,
                authenticated: this.authenticated,
                userId: this.userId
            });
        });
    }
});
