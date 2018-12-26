'use strict';

W.ns('W.pages.search.vt');

W.pages.search.vt.SearchWizardStep = W.common.WizardStep.extend({

    currentEffectName: '',
    popupDismissed: false,
    settingName_NeverShowPopupAgain: 'search_vt_donotshowagain',

    init: function init(options) {
        this._super({
            step: options.step,
            model: options && options.model,
            submit_el: options && options.submit_el,
            template_el: options && options.template_el
        });

        this.currentUserId = options && options.currentUserId;
        this.settings = new W.users.UserSettings({ userId: this.currentUserId });

        if (!this.currentUserId) {
            this.settings.remove(this.settings.settingName_WizardSearch);
        }

        this.skip_el = options && options.skip_el;
        this.back_el = options && options.back_el;
    },

    initEventHandlers: function initEventHandlers() {
        var that = this;

        $(this.submit_el).on('click', function (e) {
            e.preventDefault();
            if (that.validate()) {
                that.submit();
            }
        });

        $(this.skip_el).on('click', function (e) {
            e.preventDefault();
            that.skip();
        });

        $(this.back_el).on('click', function (e) {
            e.preventDefault();
            that.back();
        });

        $(document).on('click touchstart', function (e) {
            var elem = $(e.target);
            if (!(elem.parents('.form-field').length || elem.hasClass('.form-field'))) {
                that.closeAllEffectBoxes();
            }
        });
    },

    validate: function validate() {
        return true;
    },

    skip: function skip() {
        throw new Error('Child class must implement skip.');
    },

    back: function back() {
        throw new Error('Child class must implement back before use.');
    },

    restoreState: function restoreState() {
        throw new Error('Child class must implement restoreState.');
    },

    showDialogOrProceed: function showDialogOrProceed(container, proceedCallback) {
        var that = this;
        this.settings.get(that.settingName_NeverShowPopupAgain, function (/* setting */) {
            // TODO do not show the dialog for now (changed under WEED-201)
            /*var doNotShowAgain = setting && setting.doNotShowAgain;
             if (container[container.length - 1].value === 1 && !that.popupDismissed && !doNotShowAgain) {
             that.showJustASecondDialog();
             } else {
             proceedCallback();
             }*/

            proceedCallback();
        });
    },

    showJustASecondDialog: function showJustASecondDialog() {
        var that = this,
            $justASecondDialog = $('.just-a-second-dialog');

        $justASecondDialog.find('.dismiss-btn').on('click', function () {
            $justASecondDialog.dialog('close');
            that.popupDismissed = true;
        });

        W.common.Dialog($justASecondDialog, function () {
            that.popupDismissed = false;
            that.update(that.settingName_NeverShowPopupAgain, {
                doNotShowAgain: $('#do-not-show-again').is(':checked')
            });
        });
    },

    restoreEffectsState: function restoreEffectsState(step, container) {
        var state = this.model.get(step);
        if (!state || state.skipped) {
            return;
        }

        container.length = 0;

        var that = this;
        $.each(state.effects, function (index, effect) {
            var $effect = $('#{0}'.format(effect.name)),
                $parent = $effect.parent(),
                $importanceValue = $parent.find('.importance-value');

            $effect.addClass('active');
            $parent.find('.removable').removeClass('hidden');
            $importanceValue.removeClass('hidden');
            $importanceValue.text(effect.value);
            container.push({
                name: effect.name,
                value: effect.value
            });
        });

        if (container.length > 0) {
            that.toggleButtonsState(container);
            that.currentEffectName = container[container.length - 1].name;
        }

        if (step !== 4 && container.length === 5) {
            that.disableNotActiveEffects();
        }
    },

    toggleButtonsState: function toggleButtonsState(container) {
        if (container.length > 0) {
            $(this.submit_el).removeAttr('disabled');
            $(this.skip_el).attr('disabled', 'disabled');
        }
    },

    isStepSkipped: function isStepSkipped(step) {
        var data = this.model.get(step);
        return data && data.skipped;
    },

    disableNotActiveEffects: function disableNotActiveEffects() {
        var $vtEffects = $('.vt-effect');
        for (var i = 0; i < $vtEffects.length; i++) {
            var $el = $($vtEffects[i]);
            if (!$el.hasClass('active')) {
                $el.addClass('disabled');
            }
        }
    },

    clickVtEffect: function clickVtEffect(container) {
        var that = this;
        $('.vt-effect').on('click', function () {
            that.popupDismissed = false;

            var $effect = $(this),
                effectName = $effect.attr('id'),
                presentEffect = container.filter(function (effect) {
                    return effect.name === effectName;
                });

            if ($effect.hasClass('selected')) {
                that.closeEffectBox($('.{0}-config-box'.format(effectName)), $effect);
                return;
            }

            that.closeAllEffectBoxes();

            $effect.addClass('selected');
            that.currentEffectName = effectName;

            if (presentEffect.length > 0) {
                that.showConfigBox($effect, effectName, container, $effect.parent().find('.importance-value').text());
                return;
            }

            if (container.length <= 4) {
                $effect.addClass('active');
                $effect.parent().find('.removable').removeClass('hidden');
                $effect.parent().find('.importance-value').removeClass('hidden');
                container.push({
                    name: $effect.attr('id'),
                    value: 1
                });
            }

            if (container.length === 5) {
                that.disableNotActiveEffects();
            }

            if (container.length === 0 && that.isStepSkipped(2)) {
                $(that.submit_el).attr('disabled', 'disabled');
                $(that.skip_el).attr('disabled', 'disabled');
            }

            that.toggleButtonsState(container);
            that.showConfigBox($effect, effectName, container);
        });
    },

    showConfigBox: function showConfigBox($effect, effectName, container, effectValue) {
        var that = this,
            $configBox = $('.{0}-config-box'.format(effectName)),
            $sliderWrapper = $configBox.find('.slider-wrapper'),
            sliderValue = effectValue || 1;

        $configBox.removeClass('hidden');
        $sliderWrapper.removeClass('hidden');
        $sliderWrapper.find('.slider').slider({
            value: sliderValue, min: 1, max: 5, step: 1,
            slide: function (event, ui) {
                that.handleSlideChange(ui.value, container, $sliderWrapper);
            }
        }).each(function () {
            // Add labels to slider whose values are specified by min, max and whose step is set to 1
            var $slider = $(this),
                opt = $slider.data().uiSlider.options, // Get the options for this slider
                vals = opt.max - opt.min; // Get the number of possible values

            // Space out values
            for (var i = 0; i <= vals; i++) {
                var el = $('<label class="point point-{0}">{1}</label>'.format(i + 1, i + 1)).css('left', '{0}%'.format(i / vals * 100));
                $slider.append(el);
            }
        });

        $sliderWrapper.find('.label-{0}'.format(sliderValue)).removeClass('hidden');
        var $activePoint = $sliderWrapper.find('.point-{0}'.format(sliderValue));
        $activePoint.addClass('active');

        var left = $activePoint.css('left');
        $('.arrow-down').css('left', left === '0px' ? '5%' : left);

        $effect.parent().find('.importance-value').addClass('selected');
        $effect.parent().find('.removable').addClass('selected');

        $('.close-box').on('click', function () {
            that.closeEffectBox($configBox, $effect);
            $(this).off('click');
        });
    },

    handleSlideChange: function handleSlideChange(value, container, $sliderWrapper) {
        var that = this;
        container.forEach(function (effect) {
            if (effect.name === that.currentEffectName) {
                var $effectValue = $('#' + that.currentEffectName).parent().find('.importance-value');
                effect.value = value;
                $effectValue.text(value);

                $('.step-label').addClass('hidden');
                $('.point').removeClass('active');

                $sliderWrapper.find('.label-{0}'.format(value)).removeClass('hidden');
                var $activePoint = $sliderWrapper.find('.point-{0}'.format(value));
                $activePoint.addClass('active');

                var left = $activePoint.css('left');
                $('.arrow-down').css('left', left === '0px' ? '5%' : left);
            }
        });
    },

    closeEffectBox: function ($configBox, $effect) {
        var $sliderWrapper = $configBox.find('.slider-wrapper');
        $sliderWrapper.addClass('hidden');
        $sliderWrapper.find('.step-label').addClass('hidden');
        $configBox.addClass('hidden');
        $effect.parent().find('.importance-value').removeClass('selected');
        $effect.parent().find('.removable').removeClass('selected');
        $effect.removeClass('selected');
    },

    closeAllEffectBoxes: function () {
        $('.effect-config-box').addClass('hidden');
        $('.vt-effect').removeClass('selected');
        $('.importance-value').removeClass('selected');
        $('.removable').removeClass('selected');
    },

    clickRemoveEffect: function clickRemoveEffect(container) {
        var that = this;
        $('.removable').on('click', function () {
            var $effectCloseBtn = $(this),
                $effect = $effectCloseBtn.parent().find('.vt-effect'),
                $importanceValue = $effectCloseBtn.parent().find('.importance-value'),
                effectName = $effect.attr('id');

            $effect.removeClass('active');
            $effectCloseBtn.addClass('hidden');
            $importanceValue.addClass('hidden');
            $importanceValue.text(1);

            for (var i = 0; i < container.length; i++) {
                if (container[i].name === effectName) {
                    container.splice(i, 1);
                    break;
                }
            }

            if (container.length < 5) {
                var $vtEffects = $('.vt-effect');
                for (var j = 0; j < $vtEffects.length; j++) {
                    $($vtEffects[j]).removeClass('disabled');
                }
            }

            if (container.length === 0) {
                that.currentEffectName = '';
                $(that.submit_el).attr('disabled', 'disabled');
                $(that.skip_el).removeAttr('disabled');
            }

            if (that.step === 3 && that.isStepSkipped(2)) {
                $(that.submit_el).attr('disabled', 'disabled');
                $(that.skip_el).attr('disabled', 'disabled');
            }
        });
    }

});