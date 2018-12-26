'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessAccount = Class.extend({

    ui: {
        $businessId: $('.business-id'),
        $businessLogo: $('.bus-logo'),
        $uploadBusinessImage: $('.upload-business-image')
    },

    init: function init() {
        this.uploadBusinessImage();
    },

    uploadBusinessImage: function uploadBusinessImage() {
        var that = this;
        this.ui.$uploadBusinessImage.on('change', function (e) {
            e.preventDefault();
            var file = $(this)[0].files[0],
                formData = new FormData();

            formData.append('file', file);
            formData.append('name', file.name);

            $.ajax({
                type: 'POST',
                url: '/api/v1/businesses/{0}/image'.format(that.ui.$businessId.val()),
                enctype: 'multipart/form-data',
                data: formData,
                processData: false,
                contentType: false,
                success: function () {
                    var preview = that.ui.$businessLogo,
                        reader = new FileReader();

                    reader.addEventListener("load", function () {
                        preview[0].src = reader.result;
                    }, false);

                    if (file) {
                        reader.readAsDataURL(file);
                    }
                },
                error: function () {

                }
            });
        });
    }

});
