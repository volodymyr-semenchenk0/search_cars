$(function(){
    // Select2 initialization for brand/model
    $('#brand').select2({ theme:'bootstrap-5', placeholder:'Оберіть марку', allowClear:true, width:'100%' });
    $('#model').select2({ theme:'bootstrap-5', placeholder:'Оберіть модель', allowClear:true, width:'100%' });

    // Load models on brand change
    $('#brand').on('change', function() {
        const make = $(this).val();
        const modelSelect = $('#model');
        modelSelect.prop('disabled', true).html('<option value="">Завантаження…</option>');
        if (!make) {
            modelSelect.html('<option value="">Оберіть модель</option>');
            return;
        }
        $.getJSON(`/api/models?make=${make}`, data => {
            let opts = '<option value="">Оберіть модель</option>';
            data.forEach(m => opts += `<option value="${m.model_name}">${m.model_name}</option>`);
            modelSelect.html(opts).prop('disabled', false);
        });
    });

    // Button enable/disable logic
    const $form = $('#searchForm'), $btn = $('#searchBtn');
    const init = {
        brand:     $('#brand').val(),
        model:     $('#model').val(),
        pricefrom: $('#pricefrom').val(),
        priceto:   $('#priceto').val(),
        fregfrom:  $('#fregfrom').val(),
        fregto:    $('#fregto').val(),
        kmfrom:    $('#kmfrom').val(),
        kmto:      $('#kmto').val(),
        cy:        $('#cy').val()
    };
    function changed() {
        return Object.keys(init).some(k => $('#' + k).val() !== init[k]);
    }
    $btn.prop('disabled', !changed());
    $form.on('input change', '#brand, #model, #pricefrom, #priceto, #fregfrom, #fregto, #kmfrom, #kmto, #cy', function() {
        $btn.prop('disabled', !changed());
    });
    $form.on('submit', () => $btn.prop('disabled', true));


    // Перед сабмітом: вимикаємо порожні поля, щоб вони не потрапили в URL
    $form.on('submit', function() {
        $(this).find('select, input').each(function() {
            if (!$(this).val()) {
                $(this).prop('disabled', true);
            }
        });
    });

});
