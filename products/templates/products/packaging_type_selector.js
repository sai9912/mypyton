{% load static %}

$('[name=package_type]').on('change', function (e) {
    var self = this;
    var package_type_id = $(self).val();
    var request_url = "{% url 'products:ajax_get_package_type' '0000' %}";
    request_url = request_url.replace('0000', package_type_id);
    var image_path = "{% static 'products/site/wizard/proddesc/__CODE__.png' %}";

    $.ajax({
        url: request_url,
        cache: false,
        success: function (data) {
            image_path = image_path.replace('__CODE__', data['package_type']['code']);
            $('#bar_placement_img').attr('src', image_path);
            $('#description').html(data['package_type']['description']);
        },
        error: function () {
            $('#bar_placement_img').attr('src', '#');
            $('#description').html('Error');
        }
    });

});
