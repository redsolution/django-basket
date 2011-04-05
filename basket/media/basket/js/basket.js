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
}

