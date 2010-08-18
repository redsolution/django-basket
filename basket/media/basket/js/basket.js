;
$(document).ready(function() {
	$('#refresh-basket').click(function() {
		$(this).after('<input type="hidden" name="ajax" value="1">');
	});
});

var basket={};
basket.add_to_basket = function add_to_basket(item_id) {
	$.post('/basket/add/', {'item': item_id}, function (){
		basket.reload_basket();
	});
	return false;
};

basket.reload_basket = function reload_basket() {
	var loading_div = $('.loading').clone();
	$('#basket_panel p').prepend(loading_div);
	loading_div.show();
	$('#basket_panel').load('/basket/ajax/', null, function(){
		loading_div.hide();
	});
	return false;
};
