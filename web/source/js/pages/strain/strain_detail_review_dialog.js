'use strict';

W.ns('W.pages.vt');

W.pages.vt.VtReviewDialog = Class.extend({

    reviewEffects: [],

    effectNames: W.common.Constants.effectNames,
    benefitNames: W.common.Constants.benefitNames,
    sideEffectNames: W.common.Constants.sideEffectNames,

    dialogSubtitles: {
        'positive-effects': 'Positive Effects',
        'medical-benefits': 'Medical Benefits',
        'negative-effects': 'Negative Effects'
    },

    init: function init(options) {
        this.model = options && options.model || new W.common.Model();
        this.effectType = null;
        this.clickDisagreeLink();
    },

    clickDisagreeLink: function clickDisagreeLink() {
        var that = this;
        this.vtReviewDialogTemplate = _.template($('#vt_review_dialog_template').html());
        $('.disagree').on('click', function (e) {
            e.preventDefault();
            that.buildAndShowReviewDialog($(this));
        });

        $('.undo-disagree').on('click', function (e) {
            e.preventDefault();
            that.buildAndShowUndoDialog($(this));
        });
    },

    buildAndShowReviewDialog: function buildAndShowReviewDialog($link) {
        var that = this,
            effectType = $link.prop('id'),
            parentWidth = $('.vt-effects').outerWidth(true),
            dialogWidth = parseInt(parentWidth, 10),

            effects = 'positive-effects' === effectType ?
                this.model.get('vt').effects :
                'medical-benefits' === effectType ?
                    this.model.get('vt').benefits :
                    this.model.get('vt').side_effects,

            toDisplay = this.buildEffectsToDisplay(effects, 'positive-effects' === effectType ?
                this.effectNames : 'medical-benefits' === effectType ? this.benefitNames : this.sideEffectNames);

        this.effectType = effectType;

        $('.vt-review-dialog-wrapper').html(this.vtReviewDialogTemplate({
            subtitle: this.dialogSubtitles[effectType],
            effects: toDisplay,
            renderReviewEffect: that.renderReviewEffect
        }));

        this.initReviewDialogSliders(effectType);

        W.common.ReviewDialog($('.vt-review-dialog'), function () {
            $('.vt-review-dialog').dialog('destroy');
            that.reviewEffects = [];
        }, {
            width: '{0}px'.format(dialogWidth),
            maxWidth: '{0}px'.format(dialogWidth),
            minHeight: '300px'
        });

        this.initAddButton(effectType);
        this.clickRemoveEffect($('.remove-effect'));
        this.createVtReview();
    },

    buildAndShowUndoDialog: function buildAndShowUndoDialog($link) {
        var effectType = $link.prop('id'),
            $undoDialog = $('.undo-vt-review-dialog');

        effectType = 'positive-effects' === effectType ?
            'effects' : 'medical-benefits' === effectType ? 'benefits' : 'side_effects';

        $undoDialog.find('.btn-yes').on('click', function () {
            $.ajax({
                method: 'DELETE',
                url: '/api/v1/search/vt/{0}/ratings'.format($('.vt-id').val()),
                data: JSON.stringify({effect_type: effectType}),
                success: function () {
                    $undoDialog.dialog('close');
                    $undoDialog.find('.btn-yes').off('click');
                    window.location.reload();
                }
            });
        });

        $undoDialog.find('.btn-cancel').on('click', function () {
            $undoDialog.dialog('close');
        });

        W.common.ConfirmDialog($undoDialog);
    },

    // TODO not used now, but will be used when page refresh will be removed
    recalculateSRXScore: function recalculateSRXScore() {
        var $scoreContainer = $('.score-value'),
            $percentSign = $('.percent-sign');

        $scoreContainer.html(W.common.Constants.html.loader);
        $percentSign.addClass('hidden');

        // Give here a 1 sec delay to let backend update all necessary entities
        setTimeout(function () {
            $.ajax({
                method: 'GET',
                url: '/api/v1/search/vt/{0}/srx_score'.format($('.vt-id').val()),
                success: function (data) {
                    if (data && data.srx_score) {
                        $scoreContainer.html(data.srx_score);
                        $percentSign.removeClass('hidden');
                    }
                }
            });
        }, 1000);
    },

    buildEffectsToDisplay: function buildEffectsToDisplay(rawEffects, effectNames) {
        var effectsToDisplay = [];
        $.each(rawEffects, function (name, value) {
            if (value > 0) {
                effectsToDisplay.push({name: name, displayName: effectNames[name], value: value});
            }
        });
        effectsToDisplay.sort(this.sortValues);
        return effectsToDisplay;
    },

    buildEffectsToDisplayOnDetailPage: function buildEffectsToDisplayOnDetailPage(rawEffects, userCriteria, effectNames) {
        var effectsToDisplay = [];
        $.each(rawEffects, function (name, value) {
            if (value > 0) {
                effectsToDisplay.push({name: effectNames[name], value: value});
            }
        });
        effectsToDisplay.sort(this.sortValues);
        return effectsToDisplay;
    },

    sortValues: function sortValues(el1, el2) {
        var aName = el1.name, bName = el2.name,
            aValue = el1.value, bValue = el2.value;
        return aValue > bValue ? -1 : aValue < bValue ? 1 : aName < bName ? -1 : aName > bName ? 1 : 0;
    },

    renderReviewEffect: function renderReviewEffect(effect) {
        var template = _.template($('#vt_review_dialog_review_effect_template').html());
        return template({effect: effect});
    },

    initReviewDialogSliders: function initReviewDialogSliders(effectType) {
        var that = this;
        $.each($('.review-effect-wrapper'), function () {
            that.initReviewDialogSlider($(this), effectType);
        });

        $('.action-plus').on('click', function () {
            that.increaseEffectValue($(this), effectType);
        });

        $('.action-minus').on('click', function () {
            that.decreaseEffectValue($(this), effectType);
        });
    },

    increaseEffectValue: function increaseEffectValue($actionPlusBtn, effectType) {
        var $reviewEffectSlider = $actionPlusBtn.parent(),
            $effectSlider = $reviewEffectSlider.parent(),
            valueElements = $reviewEffectSlider.find('.value'),
            effectName = $effectSlider.parent().find('.effect-name').prop('id'),
            effectCurrentValue = parseInt($effectSlider.find('.effect-value').text(), 10),
            effectNewValue = this.buildNewIncreaseValue(effectCurrentValue, effectType);

        this.setReviewEffectValue(effectName, effectNewValue);
        $effectSlider.find('.effect-value').text(effectNewValue);

        for (var i = 0; i < valueElements.length; i++) {
            var $el = $(valueElements[i]);
            if (!$el.hasClass('active')) {
                $el.addClass('active');
                break;
            }
        }
    },

    buildNewIncreaseValue: function buildNewIncreaseValue(currentValue, effectType) {
        if (effectType === 'negative-effects') {
            if (currentValue === 0) {
                currentValue = 5;
            }
            return currentValue < 10 ? currentValue + 1 : currentValue;
        }

        return currentValue < 5 ? currentValue + 1 : currentValue;
    },

    decreaseEffectValue: function decreaseEffectValue($actionMinusBtn, effectType) {
        var $reviewEffectSlider = $actionMinusBtn.parent(),
            $effectSlider = $reviewEffectSlider.parent(),
            valueElements = $reviewEffectSlider.find('.value'),
            effectName = $effectSlider.parent().find('.effect-name').prop('id'),
            effectCurrentValue = parseInt($effectSlider.find('.effect-value').text(), 10),
            effectNewValue = this.buildNewDecreaseValue(effectCurrentValue, effectType);

        this.setReviewEffectValue(effectName, effectNewValue);
        $effectSlider.find('.effect-value').text(effectNewValue);

        for (var i = valueElements.length - 1; i >= 0; i--) {
            var $el = $(valueElements[i]);
            if ($el.hasClass('active')) {
                $el.removeClass('active');
                break;
            }
        }
    },

    buildNewDecreaseValue: function buildNewDecreaseValue(currentValue, effectType) {
        if (effectType === 'negative-effects') {
            if (currentValue === 6) {
                currentValue = 0;
            }
            return currentValue > 0 ? currentValue - 1 : currentValue;
        }

        return currentValue > 0 ? currentValue - 1 : currentValue;
    },

    initReviewDialogSlider: function initReviewDialogSlider($reviewEffectWrapper, effectType) {
        var effectName = $reviewEffectWrapper.find('.effect-name').prop('id'),
            effectValue = parseInt($reviewEffectWrapper.find('.effect-slider').find('.effect-value').text(), 10),
            effectSliderTemplate = _.template($('#vt_review_dialog_effect_slider_template').html());

        this.reviewEffects.push({name: effectName, value: effectValue});
        $reviewEffectWrapper.find('.effect-slider').append(effectSliderTemplate({
            value: this.buildDisplayValue(effectValue, effectType)
        }));
    },

    buildDisplayValue: function buildDisplayValue(value, effectType) {
        if (effectType === 'negative-effects') {
            if (value === 6) {
                value = 1;
            }

            if (value === 7) {
                value = 2;
            }

            if (value === 8) {
                value = 3;
            }

            if (value === 9) {
                value = 4;
            }

            if (value === 10) {
                value = 5;
            }
        }

        return value;
    },

    getReviewEffectValue: function (name) {
        var e = null;
        $.each(this.reviewEffects, function (index, effect) {
            if (name === effect.name) {
                e = effect;
            }
        });
        return e;
    },

    setReviewEffectValue: function (name, value) {
        $.each(this.reviewEffects, function (index, effect) {
            if (name === effect.name) {
                effect.value = value;
            }
        });
    },

    initAddButton: function initAddButton(effectType) {
        var that = this;
        this.retrieveEffects(effectType, function (effects) {
            var payloadTemplate = _.template($('#vt_review_dialog_effects_payload_template').html());
            $('.effects-payload').html(payloadTemplate({effects: effects}));

            $('.btn-add-effect').on('click', function (e) {
                e.preventDefault();
                $('.effects-payload').toggleClass('hidden');
                $('.effects-payload-top-border').toggleClass('hidden');
            });

            that.initEffectPayloadEventHandlers();
        });
    },

    retrieveEffects: function retrieveEffects(effectType, success) {
        var type = 'positive-effects' === effectType ?
            'effect' : 'medical-benefits' === effectType ? 'benefit' : 'side_effect';
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/effect/{0}'.format(type),
            success: function (effects) {
                success(effects);
            }
        });
    },

    initEffectPayloadEventHandlers: function initEffectPayloadEventHandlers() {
        var that = this;
        $('.payload-effect').on('click', function () {
            that.selectEffectPayload($(this));
        });
    },

    selectEffectPayload: function selectEffectPayload($activePayload) {
        if ($activePayload && $activePayload.length > 0) {
            var that = this,
                effectName = $activePayload.find('.effect-name').text(),
                effect = this.getReviewEffectValue(effectName);

            $('.error-message').text('');

            if (effect === null) {
                $('.review-effects-holder').append(this.renderReviewEffect({
                    displayName: $activePayload.find('.effect-display-name').text(),
                    name: effectName,
                    value: 0
                }));

                var $reviewEffectWrapper = $('.review-effect-wrapper-{0}'.format(effectName));
                this.initReviewDialogSlider($reviewEffectWrapper, that.effectType);

                $reviewEffectWrapper.find('.action-plus').on('click', function () {
                    that.increaseEffectValue($(this), that.effectType);
                });

                $reviewEffectWrapper.find('.action-minus').on('click', function () {
                    that.decreaseEffectValue($(this), that.effectType);
                });

                $reviewEffectWrapper.find('.remove-effect').on('click', function () {
                    that.removeEffect($(this));
                });
            } else {
                $('#{0}'.format(effectName)).parent().effect("highlight", {color: '#bbe6d1'}, 1000);
            }

            $('.effects-payload').addClass('hidden');
            $('.effects-payload-top-border').addClass('hidden');
        }
    },

    clickRemoveEffect: function clickRemoveEffect($removeEffect) {
        var that = this;
        $removeEffect.on('click', function () {
            that.removeEffect($(this));
        });
    },

    removeEffect: function removeEffect($removeEffect) {
        var effectName = $removeEffect.prop('id');
        for (var i = 0; i < this.reviewEffects.length; i++) {
            if (this.reviewEffects[i].name === effectName) {
                this.reviewEffects.splice(i, 1);
                break;
            }
        }
        $('.review-effect-wrapper-{0}'.format(effectName)).remove();
    },

    createVtReview: function createVtReview() {
        var that = this,
            effectType = 'positive-effects' === this.effectType ?
                'effects' : 'medical-benefits' === this.effectType ? 'benefits' : 'side_effects';

        $('.btn-update-effects').on('click', function (e) {
            e.preventDefault();
            if (that.reviewEffects.length > 0) {
                $.ajax({
                    method: 'POST',
                    url: '/api/v1/search/vt/{0}/ratings'.format($('.vt-id').val()),
                    dataType: 'json',
                    data: JSON.stringify({type: effectType, effects: that.reviewEffects}),
                    success: function () {
                        $('.vt-review-dialog').dialog('close');
                        window.location.reload();
                    }
                });
            } else {
                $('.error-message').text('At least one effect is required');
            }
        });
    },

    changeEffectNames: function changeEffectNames(namesMap) {
        var effectsToDisplay = [];
        $.each(this.reviewEffects, function (index, effect) {
            if (effect.value > 0) {
                effectsToDisplay.push({name: namesMap[effect.name], value: effect.value});
            }
        });
        effectsToDisplay.sort(this.sortValues);
        return effectsToDisplay;
    },

    effectHtml: function effectHtml(toDisplay) {
        var template = _.template($('#vt_effects').html());
        return template({
            'effects': toDisplay,
            'effectFillHtml': this.effectFillHtml,
            'userCriteriaFillHtml': function () {
            }
        });
    },

    sideEffectHtml: function sideEffectHtml(toDisplay) {
        var template = _.template($('#vt_side_effects').html());
        return template({
            'effects': toDisplay,
            'sideEffectFillHtml': this.sideEffectFillHtml,
            'userCriteriaFillHtml': function () {
            }
        });
    },

    effectFillHtml: function effectFillHtml(effectValue) {
        var fillWidth = effectValue * 0.2 * 100; // 1 point should take 20% of parent width
        return '<span class="fill" style="width: {0}%"></span>'.format(fillWidth);
    },

    sideEffectFillHtml: function sideEffectFillHtml(effectValue) {
        var fillWidth = (effectValue >= 6 ? effectValue - 5 : effectValue) * 0.2 * 100; // 1 point should take 20% of parent width
        return '<span class="fill" style="width: {0}%"></span>'.format(fillWidth);
    }
});
