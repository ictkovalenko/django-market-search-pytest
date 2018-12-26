'use strict';

W.ns('W.pages.search.vt');

W.pages.search.vt.SearchWizardStep1 = W.pages.search.vt.SearchWizardStep.extend({

    checkedTypes: [],

    init: function init(options) {
        this._super({
            step: 1,
            model: options && options.model,
            submit_el: '.btn-step-1',
            skip_el: '.btn-skip-1',
            template_el: '#search-wizard-step1',
            currentUserId: options.currentUserId
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();
        this.clickTypeCheckbox();
        this.clickTypeInfo();
        this.clickResetSearch();
    },

    clickTypeCheckbox: function clickTypeCheckbox() {
        var that = this;
        $('input[type="checkbox"]').on('click', function () {
            var $checkbox = $(this);
            if ($checkbox.is(':checked')) {
                that.checkedTypes.push($checkbox.attr('name'));
            } else {
                for (var i = 0; i < that.checkedTypes.length; i++) {
                    if (that.checkedTypes[i] === $checkbox.attr('name')) {
                        that.checkedTypes.splice(i, 1);
                        break;
                    }
                }
            }

            that.toggleButtonsState();
        });
    },

    clickTypeInfo: function clickTypeInfo() {
        $('.type-info').on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.' + $(this).parent().find('.type').attr('id') + '-dialog'), null, {
                width: 370,
                height: 300
            });
        });
    },

    clickResetSearch: function clickResetSearch() {
        var that = this,
            userId = $('.current-user-id').val();

        $('.btn-reset-search').on('click', function () {
            that.model.setData({});
            that.checkedTypes.length = 0;
            that.toggleButtonsState();
            $('input[type="checkbox"]').prop('checked', false);
            $(this).attr('disabled', 'disabled');

            that.settings.update(that.settings.settingName_WizardSearch, that.model.getData());
            $.ajax({method: 'DELETE', url: '/api/v1/users/{0}/searches'.format(userId)});
        });
    },

    renderHTML: function renderHTML() {
        return this.$template({previousSearchData: this.model.get(this.step)});
    },

    submit: function submit() {
        var data = {
            step: this.step,
            data: {
                sativa: $('input[name="sativa"]').is(":checked"),
                hybrid: $('input[name="hybrid"]').is(":checked"),
                indica: $('input[name="indica"]').is(":checked")
            }
        };
        window.history.pushState(data, 'search-step-1', '/search/vt/wizard/#2');
        $.publish('update_step_data', data);
        $.publish('show_step', {step: 2});
    },

    skip: function skip() {
        var data = {step: this.step, data: {skipped: true}};
        window.history.pushState(data, 'search-step-1', '/search/vt/wizard/#2');
        $.publish('update_step_data', data);
        $.publish('show_step', {step: 2});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            var step1State = this.model.get(this.step);
            if (!step1State || step1State.skipped) {
                return;
            }

            this.checkedTypes.length = 0;

            if (step1State.sativa) {
                $('input[name="sativa"]').prop('checked', 'checked');
                this.checkedTypes.push('sativa');
            }

            if (step1State.hybrid) {
                $('input[name="hybrid"]').prop('checked', 'checked');
                this.checkedTypes.push('hybrid');
            }

            if (step1State.indica) {
                $('input[name="indica"]').prop('checked', 'checked');
                this.checkedTypes.push('indica');
            }

            this.toggleButtonsState();
        }
    },

    toggleButtonsState: function toggleButtonsState() {
        var $submitBtn = $(this.submit_el),
            $skipBtn = $(this.skip_el);

        if (this.checkedTypes.length > 0) {
            $submitBtn.removeAttr('disabled');
            $skipBtn.attr('disabled', 'disabled');
        } else {
            $submitBtn.attr('disabled', 'disabled');
            $skipBtn.removeAttr('disabled');
        }
    }

});