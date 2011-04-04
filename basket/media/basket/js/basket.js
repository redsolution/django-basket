var basket = {};

basket.add = function(el, content_type_id, object_id){
	basket.on_add_click(el);
	$.post('basket.add_url',{
		'content_type': content_type,
		'object_id': object_id
		}, basket.on_add_sucecss
	);
}