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
    $('#dutyForm').on('submit', function(){
        $('#loader').removeClass('d-none').addClass('d-flex');
    });
    $(window).on('load', function(){
        $('#loader').removeClass('d-flex').addClass('d-none');
    });
});

let deleteModal = document.getElementById('deleteModal');
deleteModal.addEventListener('show.bs.modal', function (event) {
    // Кнопка, яка викликала модал
    let btn = event.relatedTarget;
    let carId = btn.getAttribute('data-car-id');

    // Змінюємо action форми всередині модала
    let form = document.getElementById('deleteModalForm');
    form.action = '/cars/' + carId + '/delete';
});


$(function () {
    const compareBtn = $('#compareBtn');
    const resetBtn = $('#resetBtn');
    const table = $('#carsTable');

    // Парсимо початкові ids з URL
    const urlParams = new URLSearchParams(window.location.search);
    const initialIds = urlParams.get('ids') ? urlParams.get('ids').split(',') : [];

    // Встановлюємо чекбокси за початковим вибором
    table.find('.compare-checkbox').each(function () {
        if (initialIds.includes(this.value)) $(this).prop('checked', true);
    });

    // Оновити стан кнопки
    function updateCompareButton() {
        const checked = table.find('.compare-checkbox:checked').length;
        compareBtn.prop('disabled', checked < 2);
    }

    // Початковий стан
    updateCompareButton();

    // Обробник зміни чекбоксів
    table.on('change', '.compare-checkbox', updateCompareButton);

    // Натискання на "Порівняти"
    compareBtn.on('click', function () {
        const ids = table.find('.compare-checkbox:checked').map(function () { return this.value; }).get();
        const query = ids.length ? `?ids=${ids.join(',')}` : '';
        window.location.href = `/compare${query}`;
    });

    // Скинути всі вибрані
    resetBtn.on('click', function () {
        table.find('.compare-checkbox').prop('checked', false);
        updateCompareButton();
        // Видалити параметр ids з URL без перезавантаження
        urlParams.delete('ids');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.replaceState(null, '', newUrl);
    });
});