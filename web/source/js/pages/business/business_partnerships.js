'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessPartnerships = Class.extend({
    init: function init(options) {
        this.businessId = options.businessId;
        this.partnerships = [];
        this.newPartner = undefined;

        this.ui = {
            $locations: $('#locations'),
            $partners: $('.partners'),
            $addBtn: $('#add-partnership'),
            $input: $('#disp-lookup')
        };
        this.template = _.template($('#partnership-template').html());

        this.fetchDispensaries();
        this.ui.$locations.on('change', this.fetchDispensaries.bind(this));
        this.ui.$addBtn.on('click', this.onAddButtonClick.bind(this));

        this.initDispensaryLookup();
    },

    fetchDispensaries: function fetchDispensaries() {
        var that = this,
            urlTemplate = '/api/v1/businesses/{0}/locations/{1}/partnerships?grower_id={2}',
            growerId = that.ui.$locations.val();

        return $.ajax({
            method: 'GET',
            url: urlTemplate.format(that.businessId, growerId, growerId),
            success: function (data) {
                that.partnerships = data.partnerships;
                that.renderPartnerships(that.partnerships);
                $('.delete-partner').on('click', that.onPartnershipDelete.bind(that));
            }
        });
    },

    onAddButtonClick: function onAddButtonClick() {
        var that = this;

        that.ui.$addBtn.prop('disabled', true);
        that.ui.$addBtn.text('Adding ...');

        that.createPartnership(that.newPartner).success(function() {
            that.fetchDispensaries().success(function() {
                that.ui.$addBtn.text('Add');
                that.ui.$input.val('');

                that.newPartner = undefined;
            });
        })
    },

    onPartnershipDelete: function onPartnershipDelete(e) {
        var that = this,
            businessId = that.businessId,
            locationId = that.ui.$locations.val(),
            $target = $(e.currentTarget),
            partnershipId = $target.attr('data-partnership-id');

        $target.prop('disabled', true);
        $target.css('color', '#ff4646');

        return $.ajax({
            method: 'DELETE',
            url: '/api/v1/businesses/{0}/locations/{1}/partnerships/{2}'.format(businessId, locationId, partnershipId)
        }).success(that.fetchDispensaries.bind(that));
    },

    initDispensaryLookup: function initDispensaryLookup() {
        var that = this;
        var DispensaryLookup = W.pages.locations.LocationsLookupWidget;
        new DispensaryLookup({
            locationType: 'dispensary',
            onChange: function(dispensary) {
                that.newPartner = dispensary;
                that.ui.$addBtn.prop('disabled', !Boolean(dispensary));
            }});
    },

    renderPartnerships: function renderPartnerships(partnerships) {
        this.ui.$partners.html(this.template({ partnerships: partnerships }));
    },

    createPartnership: function createPartnership(dispensary) {
        var businessId = this.businessId,
            locationId = this.ui.$locations.val();

        return $.ajax({
            method: 'POST',
            url: '/api/v1/businesses/{0}/locations/{1}/partnerships'.format(businessId, locationId),
            data: JSON.stringify({ dispensary_id: dispensary.id })
        });
    }

});
