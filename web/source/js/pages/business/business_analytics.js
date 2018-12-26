'use strict';

W.ns('W.pages.business');

W.pages.business.Analytics = Class.extend({

    ui: {
        $datePickerRange: $("#reportrange")
    },

    init: function init() {
        this.configureDatePicker();
    },

    configureDatePicker: function(){

        this.ui.$datePickerRange.on("apply.daterangepicker", function(ev, picker){

            window.location.href = window.location.pathname + "?from_date={1}&to_date={0}".format(
                picker.endDate.format('YYYY-MM-DD'),
                picker.startDate.format('YYYY-MM-DD')
            );
        });

        var start = moment().subtract(7, 'days');
        var end = moment();

        if(window.location.href.indexOf("?") > -1) {
            var qs = W.qs(window.location.href);
            start = moment(qs.from_date) || end;
            end = moment(qs.to_date) || start;
        }

        function cb(start, end) {
            $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        }

        this.ui.$datePickerRange.daterangepicker({
            startDate: start,
            endDate: end,
            ranges: {
               'Today': [moment(), moment()],
               'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
               'Last 7 Days': [moment().subtract(6, 'days'), moment()],
               'Last 14 Days': [moment().subtract(13, 'days'), moment()],
               'Last 30 Days': [moment().subtract(29, 'days'), moment()],
               'This Month': [moment().startOf('month'), moment().endOf('month')],
               'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
            }
        }, cb);

        cb(start, end);
    },

    parseData: function (data) {
        var len = data.length,
            startDate = this.ui.$datePickerRange.data('daterangepicker').startDate,
            endDate = this.ui.$datePickerRange.data('daterangepicker').endDate,
            obj, end, start, range = [], j, date;

        if (data && typeof data === 'object' && len) {

            // if there are no data between start date from datepicker and first date from data fill with zero.
            start = moment(data[0].day);
            date = moment(startDate).subtract(1, 'days');
            for (j = 1; j < start.diff(startDate, 'days') + 1; j += 1) {
                range.push([date.add(1, 'days').format('YYYY-MM-DD'), 0])
            }

            for (var i = 0; i < len; i += 1) {
                obj = data[i];
                end = i + 1 < len && moment(data[i + 1].day);
                start = moment(obj.day);
                range.push([obj.day, obj.count]);

                if (end && end.diff(start, 'days') > 1) {
                    // if there are no data between two dates fill skipped dates with zero.
                    for (j = 1; j < end.diff(start, 'days') - 1; j += 1) {
                        range.push([start.add(1, 'days').format('YYYY-MM-DD'), 0])
                    }
                }
            }

            // if there are no data between end date from datepicker and last date from data fill with zero.
            end = moment(data[len - 1].day);
            date = moment(data[len - 1].day);
            for (j = 1; j < endDate.diff(end, 'days') + 1; j += 1) {
                range.push([date.add(1, 'days').format('YYYY-MM-DD'), 0])
            }
        }
        return range
    },

    drawCharts: function(data, selector, title, subtitle, yAxisTitle, color) {
      Highcharts.chart(selector, {
            title: {
                text: title
            },
            subtitle: {
                text: subtitle
            },
            xAxis: {
                type:"category",
                labels: {
                   rotation: 20
                }
            },
            yAxis: {
                title: {
                    text: yAxisTitle || 'Views'
                },
                tickInterval: 1
            },
            series: [{
                name: yAxisTitle || 'Views',
                data: this.parseData(data || []),
                color: color || '#2f7ed8'
            }],
            responsive: {
                rules: [{
                    condition: {
                        maxWidth: 500
                    },
                    chartOptions: {
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom'
                        }
                    }
                }]
            }

        });
    },

    drawBizLookupChart: function(data){
        this.drawCharts(
            data,
            'biz-lookup-chart',
            'Dispensary Page Views using Business Lookup',
            'Shows how many people viewed your dispensary page from our dispensary lookup tool'
        );
    },
    drawLookupActionChart: function(data){
        this.drawCharts(
            data,
            'biz-lookup-action-chart',
            'Dispensary Page Action using Business Lookup',
            'Shows how many people make calls or get directions from your dispensary page',
            'Actions',
            '#c42525'
        );
    },
    drawSearchChart: function(data){
        this.drawCharts(
            data,
            'search-chart',
            'Dispensary Page Views using Available At',
            'Shows how many people viewed your dispensary page from using our Available At feature on VT pages'
        )
    },

    drawUpdateRequestChart: function(data){
        this.drawCharts(
            data,
            'update-request-chart',
            'Update Requests',
            'Shows update requests count',
            'Requests'
        )
    },

    drawOutOfStockChart: function(data){
        this.drawCharts(
            data,
            'out-of-stock-chart',
            'Out of Stock Reports',
            'Shows out of stock reports count',
            'Reports'
        )
    },

    drawFeaturedImpression: function(data){
        this.drawCharts(
            data,
            'impression-chart',
            'Featured Dispensary Page Impressions',
            'Shows total times when Dispensary was seen in featured dispensaries list',
            'Impressions'
        )
    },

    drawFeaturedView: function(data){
        this.drawCharts(
            data,
            'view-chart',
            'Dispensary Page Views using featured dispensaries',
            'Shows total times when Dispensary was viewed from featured dispensaries list',
            'Views',
            '#c42525'
        )
    }

});
