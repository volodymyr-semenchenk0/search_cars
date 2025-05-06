$(function(){
    // Ініціалізація Select2 для полів
    $('#brand').select2({ theme:'bootstrap-5', placeholder:'Оберіть марку', allowClear:true, width:'100%' });
    $('#model').select2({ theme:'bootstrap-5', placeholder:'Оберіть модель', allowClear:true, width:'100%' });

    // Підтягування моделей після вибору марки
    $('#brand').on('change', function() {
        const make = $(this).val();
        const modelSelect = $('#model');
        modelSelect.prop('disabled', true).html('<option value="">Завантаження…</option>').trigger('change');

        if (!make) {
            modelSelect.html('<option value="">Оберіть модель</option>').prop('disabled', true).trigger('change');
            return;
        }
        $.getJSON(`/api/models?make=${make}`, function(data) {
            let options = '<option value="">Оберіть модель</option>';
            data.forEach(m => {
                options += `<option value="${m.model_name}">${m.model_name}</option>`;
            });
            modelSelect.html(options).prop('disabled', false).trigger('change');
        });
    });

    // Логіка кнопки "Пошук"
    const $form = $('#searchForm');
    const $searchBtn = $('#searchBtn');

    // Збережені початкові значення полів
    const initial = {
        brand: $('#brand').val(),
        model: $('#model').val(),
        fregto: $('#fregto').val(),
        kmto: $('#kmto').val(),
        cy: $('#cy').val()
    };
    // Функція перевірки, чи було змінено хоча б одне поле
    function checkChanges() {
        return $('#brand').val() !== initial.brand ||
            $('#model').val() !== initial.model ||
            $('#fregto').val() !== initial.fregto ||
            $('#kmto').val() !== initial.kmto ||
            $('#cy').val() !== initial.cy;
    }

    // Ініціальний стан кнопки
    if (initial.brand || initial.model || initial.fregto || initial.kmto || initial.cy) {
        $searchBtn.prop('disabled', false);
    } else {
        $searchBtn.prop('disabled', true);
    }

    // Дозволити кнопку після змін у полях
    $('#brand, #model, #fregto, #kmto, #cy').on('change input', function() {
        if (checkChanges()) {
            $searchBtn.prop('disabled', false);
        }
    });

    // Вимкнути кнопку при відправці форми
    $form.on('submit', function() {
        $searchBtn.prop('disabled', true);
    });
});


