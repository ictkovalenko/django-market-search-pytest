'use strict';

W.ns('W.pages.grower');

W.pages.grower.GrowerInfo = Class.extend({
    init: function init(options) {
        this.growerId = options.growerId;
        this.businessId = options.businessId;
        this.template = _.template($('#grower_partner_template').html());

        this.attachEventHandlers();
        this.fetchDispensaries();
    },

    attachEventHandlers: function attachHandlers() {
        $('.filter').on('click', this.onFilterClick);
    },

    onFilterClick: function onFilterClick(e) {
        var $currentTarget = $(e.currentTarget),
            $vt = $('.vt'),
            $vtPlaceholder = $('.vt-placeholder');

        var filter = $currentTarget.attr('data-filter');

        if (filter === 'all') {
            $vt.css('display', '');
            if ($vt.length === 0) {
                $vtPlaceholder.css('display', '');
            } else {
                $vtPlaceholder.css('display', 'none');
            }
        } else {
            $vt.css('display', 'none');
            $('.vt[data-variety="{0}"]'.format(filter)).css('display', '');

            if ($('.vt[data-variety="{0}"]'.format(filter)).length === 0) {
                $vtPlaceholder.css('display', '');
            } else {
                $vtPlaceholder.css('display', 'none');
            }
        }

        $('.filter.active').removeClass('active');
        $('.filter[data-filter="{0}"]'.format(filter)).addClass('active');
    },

    fetchDispensaries: function fetchDispensaries() {
        var that = this,
            urlTemplate = '/api/v1/businesses/{0}/locations/{1}/partnerships?grower_id={2}',
            url = urlTemplate.format(this.businessId, this.growerId, this.growerId);

        $('.section.partners .content').html('Loading ...');
        return $.ajax({
            method: 'GET',
            url: url,
            success: function (data) {
                if (data.partnerships.length > 0) {
                    that.renderPartnerships(data.partnerships);
                } else {
                    $('.section.partners .content').html(
                        'This grower does not have any ' +
                        'partnerships with dispensaries.'
                    );
                }
            }
        });
    },

    renderPartnerships: function renderPartnerships(partnerships) {
        $('.section.partners .content').html(this.template({ partnerships: partnerships }));
    }

});