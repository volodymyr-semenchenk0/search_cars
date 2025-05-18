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

const compareBtn = $('#compareBtn');
const resetBtn = $('#resetBtn');
const table = $('#carsTable');

if (table.length) {
  const urlParams = new URLSearchParams(window.location.search);
  const initialIds = urlParams.get('ids') ? urlParams.get('ids').split(',') : [];

  table.find('.compare-checkbox').each(function () {
    if (initialIds.includes(this.value)) {
      $(this).prop('checked', true);
    }
  });

  function updateCompareButton() {
    const checkedCount = table.find('.compare-checkbox:checked').length;
    compareBtn.prop('disabled', checkedCount < 1);
  }


  updateCompareButton();

  table.on('change', '.compare-checkbox', function() {
    updateCompareButton();
    const currentIds = table.find('.compare-checkbox:checked').map(function () {
      return this.value;
    }).get();

    const urlParamsHandler = new URLSearchParams(window.location.search);
    if (currentIds.length > 0) {
      urlParamsHandler.set('ids', currentIds.join(','));
    } else {
      urlParamsHandler.delete('ids');
    }
    const newUrl = window.location.pathname + '?' + urlParamsHandler.toString();

    window.history.replaceState({path: newUrl}, '', newUrl);
  });

  compareBtn.on('click', function () {
    const ids = table.find('.compare-checkbox:checked').map(function () {
      return this.value;
    }).get();

    if (ids.length > 0) {
      const currentSearchParams = new URLSearchParams(window.location.search);
      currentSearchParams.set('ids', ids.join(','));

      window.location.href = `cars/compare?${currentSearchParams.toString()}`;
    } else {
      alert('Будь ласка, оберіть автомобілі для порівняння.');
    }
  });

  resetBtn.on('click', function () {
    table.find('.compare-checkbox').prop('checked', false);
    updateCompareButton();
    const urlParamsHandler = new URLSearchParams(window.location.search);
    urlParamsHandler.delete('ids');
    const newUrl = window.location.pathname + '?' + urlParamsHandler.toString().replace(/&*$/, ""); // Видаляємо & в кінці, якщо є
    window.history.replaceState({path: newUrl}, '', newUrl);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('confirmDeleteModal');
  const deleteForm = modal?.querySelector('#deleteOfferForm');
  const offerDescriptionEl = modal?.querySelector('#offerDescriptionToDelete');
  const flashContainer = document.getElementById('flash-messages');

  let currentOfferId = null;

  if (!modal || !deleteForm || !offerDescriptionEl || !flashContainer) return;

  modal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    currentOfferId = button.getAttribute('data-offer-id');
    const description = button.getAttribute('data-offer-description');

    offerDescriptionEl.textContent = description || '';
    deleteForm.dataset.offerId = currentOfferId;
    deleteForm.action = `/cars/${currentOfferId}/delete`;
  });

  deleteForm.addEventListener('submit', async event => {
    event.preventDefault();
    if (!currentOfferId) return;

    try {
      const response = await fetch(`/cars/${currentOfferId}/delete`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      const html = await response.text();
      flashContainer.innerHTML = html;

      const row = document.getElementById(`car-row-${currentOfferId}`);
      if (row) row.remove();

      bootstrap.Modal.getInstance(modal)?.hide();
    } catch (error) {
      console.error('Помилка:', error);
      flashContainer.innerHTML = `<div class="alert alert-danger">Не вдалося видалити оголошення.</div>`;
    }
  });
});