var basket = {};
basket.add = function(el, content_type_id, object_id){
	var event = jQuery.Event("before_add.basket");
	event.el= el;
	$(document).trigger(event);
	
	$.ajax({
		'type': 'POST',
		'url': basket.add_url,
		'data': {
			'content_type': content_type_id,
			'object_id': object_id
		},
		'dataType': 'text',
		'success': function(data, textStatus) {
			var event = jQuery.Event("add_success.basket");
			event.el = el;
			event.status = textStatus;
			$(document).trigger(event, data);
		},
		'error': function(XMLHttpRequest, textStatus, errorThrown) {
			var event = jQuery.Event("add_error.basket");
			event.el = el;
			event.request = XMLHttpRequest;
			event.status = textStatus;
			$(document).trigger(event, errorThrown);
		}}
	);
	return false;
};

basket.del = function(el, content_type_id, object_id) {
	var event = jQuery.Event("before_del.basket");
	event.el= el;
	this.do_delete = true;
	$(document).trigger(event);
	
	if (this.do_delete) {
		$.ajax({
			'type': 'POST',
			'url': basket.del_url,
			'data': {
				'content_type': content_type_id,
				'object_id': object_id
			},
			'dataType': 'text',
			'success': function(data, textStatus) {
				var event = jQuery.Event("del_success.basket");
				event.el = el;
				event.status = textStatus;
				$(document).trigger(event, data);
			},
			'error': function(XMLHttpRequest, textStatus, errorThrown) {
				var event = jQuery.Event("del_error.basket");
				event.el = el;
				event.request = XMLHttpRequest;
				event.status = textStatus;
				$(document).trigger(event, errorThrown);
			}}
		);
	}
	return false;
}

$('html').ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            var i;
            for (i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
