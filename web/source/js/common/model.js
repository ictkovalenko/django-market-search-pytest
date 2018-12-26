'use strict';

W.ns('W.common');

W.common.Model = Class.extend({

    data: {},

    init: function init(data) {
        this.data = data || {};
    },

    get: function (key) {
        return this.data[key];
    },

    set: function (key, value) {
        this.data[key] = value;
    },

    getData: function getData() {
        return this.data;
    },

    setData: function setData(data) {
        this.data = data;
    }
});
