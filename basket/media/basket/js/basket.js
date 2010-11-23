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
  $('#basket-is-loading').show();
	$('#basket-summary').load('/basket/ajax/', null, function(){
    $('#basket-is-loading').hide();
	});
	return false;
};
