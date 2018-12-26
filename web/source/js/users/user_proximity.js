'use strict';

W.ns('W.users');

W.users.ProximityPage = Class.extend({

    defaultProximityValue: 10,

    ui: {
        $userId: $('.user-id'),
        $proximityInput: $('.proximity-value')
    },

    init: function (options) {
        this.proximity = options && options.proximity;

        this.initSlider();
        this.updateProximity();
    },

    initSlider: function initSlider() {
        var that = this;
        $('.slider').slider({
            range: 'min',
            value: that.proximity || that.defaultProximityValue,
            min: 0, max: 50, step: 0.5,
            slide: function (event, ui) {
                that.setSliderHandleValue(ui.value);
                that.proximity = ui.value;
                that.ui.$proximityInput.val(ui.value);
            }
        });

        this.setSliderHandleValue(this.proximity || this.defaultProximityValue);
        this.initProximityInput();
    },

    initProximityInput: function initProximityInput() {
        var that = this,
            $proximity = $('.proximity-value');

        $proximity.on('focusout', function () {
            var $input = $(this),
                $inputVal = $input.val();

            that.processProximityValueChange($inputVal);
        });

        $proximity.on('keyup', function (e) {
            if (e.keyCode === 13) { // Enter Key
                var $input = $(this),
                    $inputVal = $input.val();

                that.processProximityValueChange($inputVal);
                that.sendUpdate();
            }
        });
    },

    processProximityValueChange: function processProximityValueChange($inputVal) {
        if ($inputVal) {
            $inputVal = parseFloat($inputVal).toFixed(1);
            $('.slider').slider('value', $inputVal);
            this.proximity = $inputVal;
        } else {
            this.setProximityValue(0);
        }

        if ($inputVal && $inputVal < 0) {
            this.setProximityValue(0);
        }

        if ($inputVal && $inputVal > 50) {
            this.setProximityValue(50);
        }
    },

    setProximityValue: function setProximityValue(value) {
        $('.slider').slider('value', value);
        this.setSliderHandleValue(value);
        $('.proximity-value').val(value);
        this.proximity = value;
    },

    setSliderHandleValue: function setSliderHandleValue(value) {
        $('.proximity-value').off('focusout');
        $('.ui-slider-handle').html('<input type="number" class="proximity-value" value="{0}" title="MI">'.format(value));
        this.initProximityInput();
    },

    updateProximity: function updateProximity() {
        var that = this;
        $('.btn-update-proximity').on('click', function () {
            that.sendUpdate();
        });
    },

    sendUpdate: function sendUpdate() {
        $.ajax({
            method: 'POST',
            url: '/api/v1/users/{0}/proximity'.format(this.ui.$userId.val()),
            dataType: 'json',
            data: JSON.stringify({'proximity': this.proximity}),
            success: function () {
                window.location.reload();
            }
        });
    }

});
