$(function(){
    $('#brand').select2({ theme:'bootstrap-5', placeholder:'Оберіть марку', allowClear:true });
    $('#model').select2({ theme:'bootstrap-5', placeholder:'Оберіть модель', allowClear:true });

    $('#brand').on('change', function(){
        const make = $(this).val();
        const $model = $('#model');
        $model.prop('disabled', true).html('<option>Завантаження…</option>').trigger('change');

        if (!make) {
            $model.html('<option value="">Оберіть модель</option>').prop('disabled', true).trigger('change');
            return;
        }
        // тепер звертаємося до свого серверу
        $.getJSON(`/api/models?make=${make}`, function(data){
            let opts = '<option value="">Оберіть модель</option>';
            data.forEach(m => {
                opts += `<option value="${m.model_name}">${m.model_name}</option>`;
            });
            $model.html(opts).prop('disabled', false).trigger('change');
        });
    });
});