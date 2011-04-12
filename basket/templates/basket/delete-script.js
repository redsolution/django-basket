{% load i18n %}
function updateElementIndex(el, prefix, ndx) {
        var id_regex = new RegExp('(' + prefix + '-\\d+)');
        var replacement = prefix + '-' + ndx;
        if ($(el).attr("for")) {
            $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
        }
        if (el.id) {
            el.id = el.id.replace(id_regex, replacement);
        }
        if (el.name) {
            el.name = el.name.replace(id_regex, replacement);
        }
    }
    
    // bind delete events 
    $(document).bind("before_del.basket", function(e){
        if (basket.num_forms.val() === 1) {
            basket.do_delete = confirm("{% trans 'Are you sure about deleting last item?' %}"); 
       }
    });

    var prefix = '{{ formset.prefix }}';
    basket.num_forms = $('#id_'+prefix+'-TOTAL_FORMS');

    $(document).bind("del_success.basket", function(e, data){
        // update basket panel 
        $('#basket-summary').html(data);
        // delete row 
        $(e.el).parents('.dynamic-form').remove();

        // set new TOTAL_FORMS 
        var forms = $('.dynamic-form');
        var formCount = parseInt(basket.num_forms.val(), 10);
        basket.num_forms.val(forms.length);
        
        // update indexes and names 
        var i;
        for (i=0; i<formCount; i++) {
            $(forms.get(i)).children().not(':last').children().each(function() {
                updateElementIndex(this, prefix, i);
            });
        }

        // If basket is empty, reload page
        if (forms.length===0) {
            $('#basket_page_forms').html('<p>{% trans "Your basket is empty" %}</p>');
        }

    });
    
   $(document).bind("del_error.basket", function(e, error){
        alert('{% trans "Error occured when delete from basket:\n" %}' + error);
        window.location.reload();
    });