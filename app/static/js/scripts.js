$(function () {
  const makeSelect = $('#make');
  const modelSelect = $('#model');

  makeSelect.select2({theme: 'bootstrap-5', placeholder: 'Оберіть марку', allowClear: true});
  modelSelect.select2({theme: 'bootstrap-5', placeholder: 'Оберіть модель', allowClear: true});

  const preselectedMakeId = makeSelect.val();
  const preselectedModelId = decodeURIComponent(modelSelect.data('selected') || '');

  makeSelect.on('change', function () {
    const makeId = $(this).val();
    modelSelect.prop('disabled', true).html('<option value="">Завантаження…</option>');

    if (!makeId) {
      modelSelect.html('<option value="">Оберіть модель</option>').prop('disabled', true);
      return;
    }

    $.getJSON(`/api/models?make=${makeId}`, function (data) {
      let opts = '<option value="">Оберіть модель</option>';
      data.forEach(m => {
        // Логіка для попереднього вибору моделі
        const isSelected = (makeId === preselectedMakeId && m.id.toString() === preselectedModelId);
        opts += `<option value="${m.id}" ${isSelected ? 'selected' : ''}>${m.name}</option>`;
      });
      modelSelect.html(opts).prop('disabled', false);
    });
  });

  if (preselectedMakeId) {
    makeSelect.trigger('change');
  }
});

$(function () {
  $('#searchForm').on('submit', function () {
    $('#loader').removeClass('d-none').addClass('d-flex');
  });
  $('#dutyForm').on('submit', function () {
    $('#loader').removeClass('d-none').addClass('d-flex');
  });
  $(window).on('load', function () {
    $('#loader').removeClass('d-flex').addClass('d-none');
  });
});

// Обробник для модального вікна підтвердження видалення ОГОЛОШЕННЯ
let confirmDeleteModal = document.getElementById('confirmDeleteModal');
if (confirmDeleteModal) {
  confirmDeleteModal.addEventListener('show.bs.modal', function (event) {
    let button = event.relatedTarget;

    let offerId = button.getAttribute('data-offer-id');
    let offerDescription = button.getAttribute('data-offer-description');

    let offerDescriptionElement = confirmDeleteModal.querySelector('#offerDescriptionToDelete');
    if (offerDescriptionElement) {
      offerDescriptionElement.textContent = offerDescription;
    }

    let deleteForm = confirmDeleteModal.querySelector('#deleteOfferForm');
    if (deleteForm) {
      deleteForm.action = `/cars/${offerId}/delete`;
    }
  });
}


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
    const ids = table.find('.compare-checkbox:checked').map(function () {
      return this.value;
    }).get();
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