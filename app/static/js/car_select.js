$(function () {
    const modelSelect = $('#model');
    const preselectedMake = $('#make').val();
    const preselectedModel = decodeURIComponent(modelSelect.data('selected') || '');

    // ініціалізація Select2
    $('#make').select2({ theme: 'bootstrap-5', placeholder: 'Оберіть марку', allowClear: true });
    modelSelect.select2({ theme: 'bootstrap-5', placeholder: 'Оберіть модель', allowClear: true });

    // завантаження моделей при виборі марки
    $('#make').on('change', function () {
        const make = $(this).val();
        modelSelect.prop('disabled', true).html('<option>Завантаження…</option>').trigger('change');

        if (!make) {
            modelSelect.html('<option value="">Оберіть модель</option>').prop('disabled', true).trigger('change');
            return;
        }

        $.getJSON(`/api/models?make=${make}`, function (data) {
            let opts = '<option value="">Оберіть модель</option>';
            data.forEach(m => {
                opts += `<option value="${m.model_name}">${m.model_name}</option>`;
            });
            modelSelect.html(opts).prop('disabled', false).trigger('change');

            // якщо є попередньо обрана модель — встановлюємо її
            if (make === preselectedMake && preselectedModel) {
                modelSelect.val(preselectedModel).trigger('change.select2');
            }
        });
    });

    // якщо є збережені make + model — ініціюємо завантаження моделей
    if (preselectedMake && preselectedModel) {
        $('#make').trigger('change');
    }
});

$(function(){
    $('#searchForm').on('submit', function(){
        $('#loader').removeClass('d-none').addClass('d-flex');
    });
    $(window).on('load', function(){
        $('#loader').removeClass('d-flex').addClass('d-none');
    });
});