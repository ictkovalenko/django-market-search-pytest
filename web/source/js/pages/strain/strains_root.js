'use strict';

W.ns('W.pages.vt');

W.pages.vt.VtsRootPage = Class.extend({

    currentPage: 0,
    pageSize: 8,
    vts: [],

    regions: {
        $vtsList: $('.list')
    },

    templates: {
        vtExampleItem: _.template($('#vts_example_item_template').html())
    },

    init: function init(options) {
        var that = this;

        if (options && options.type) {
            that.getVtsByType(options.type, function (data) {
                that.vts = data;
                that.regions.$vtsList.html('');
                that.showVts();
            });
        }
    },

    getVtsByType: function getVtsByType(type, success) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/vts/{0}?limit={1}'.format(type, 8),
            success: function (data) {
                success(data);
            }
        });
    },

    showVts: function showVts() {
        var that = this,
            start = this.currentPage * this.pageSize,
            page = this.vts.slice(start, start + this.pageSize),
            varieties = W.common.Constants.vtVarieties,
            Vt = this.templates.vtExampleItem;

        $.each(page, function (i, e) {
            that.regions.$vtsList.append(Vt({
                image: e.image,
                name: e.name,
                variety: e.variety,
                varietyName: varieties[e.variety],
                slug: e.slug
            }));
        });
    }

});