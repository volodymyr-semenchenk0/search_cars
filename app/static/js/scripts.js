$(function () {

  function initializeMakeModelSelects() {
    const makeSelect = $('#make');
    const modelSelect = $('#model');

    if (!makeSelect.length && !modelSelect.length) return;

    if (makeSelect.length) {
      makeSelect.select2({ theme: 'bootstrap-5', placeholder: 'Оберіть марку', allowClear: true });
    }
    if (modelSelect.length) {
      modelSelect.select2({ theme: 'bootstrap-5', placeholder: 'Оберіть модель', allowClear: true });
    }

    if (makeSelect.length && modelSelect.length) {
      const preselectedMakeId = makeSelect.val();
      const preselectedModelId = decodeURIComponent(modelSelect.data('selected') || '');

      makeSelect.on('change', function () {
        const makeId = $(this).val();
        modelSelect.prop('disabled', true).html('<option value="">Завантаження…</option>').val('').trigger('change');
        if (!makeId) {
          modelSelect.html('<option value="">Оберіть модель</option>').prop('disabled', true).trigger('change');
          return;
        }
        $.getJSON(`/api/models?make=${makeId}`, function (data) {
          let opts = '<option value="">Оберіть модель</option>';
          data.forEach(m => {
            const isSelected = (makeId === preselectedMakeId && m.id.toString() === preselectedModelId);
            opts += `<option value="${m.id}" ${isSelected ? 'selected' : ''}>${m.name}</option>`;
          });
          modelSelect.html(opts).prop('disabled', false);
          if (makeId === preselectedMakeId && preselectedModelId) {
            modelSelect.val(preselectedModelId).trigger('change');
          }
        });
      });
      if (preselectedMakeId) {
        makeSelect.trigger('change');
      } else {
        modelSelect.html('<option value="">Оберіть модель</option>').prop('disabled', true);
      }
    }
  }
  initializeMakeModelSelects();

  function initializeCountrySelect(selector) {
    const selectElement = $(selector);
    if (!selectElement.length) return;
    const preselectedValue = selectElement.val() || selectElement.data('selected-value') || '';
    selectElement.select2({
      theme: 'bootstrap-5',
      placeholder: 'Оберіть країну',
      allowClear: true,
      ajax: {
        url: '/api/countries',
        dataType: 'json',
        delay: 250,
        data: function (params) { return { q: params.term, page: params.page || 1 }; },
        processResults: function (data) {
          return { results: data.map(country => ({ id: country.code, text: country.name })) };
        },
        cache: true
      },
      minimumInputLength: 0
    });
    if (preselectedValue && selectElement.find("option[value='" + preselectedValue + "']").length) {
      selectElement.val(preselectedValue).trigger('change');
    }
  }
  initializeCountrySelect('#cy');
  initializeCountrySelect('#country');

  $('#searchForm, #dutyForm').on('submit', function () {
    $('#loader').removeClass('d-none').addClass('d-flex');
  });
  $(window).on('load', function () {
    $('#loader').removeClass('d-flex').addClass('d-none');
  });

  function initializeCompareLogic(tableId, compareButtonId, resetButtonId, checkboxClass, originPageName) {
    const compareBtn = $(compareButtonId);
    const resetBtn = $(resetButtonId);
    const table = $(tableId);

    if (!table.length || !compareBtn.length || !resetBtn.length) {
      return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const initialIds = urlParams.get('ids') ? urlParams.get('ids').split(',') : [];

    table.find('.' + checkboxClass).each(function () {
      if (initialIds.includes(this.value)) {
        $(this).prop('checked', true);
      }
    });

    function updateCompareButtonState() {
      const checkedCount = table.find('.' + checkboxClass + ':checked').length;
      compareBtn.prop('disabled', checkedCount < 1);
    }

    updateCompareButtonState();

    table.on('change', '.' + checkboxClass, function() {
      updateCompareButtonState();
      const currentIds = table.find('.' + checkboxClass + ':checked').map(function () {
        return this.value;
      }).get();
      const currentUrlParams = new URLSearchParams(window.location.search);
      if (currentIds.length > 0) {
        currentUrlParams.set('ids', currentIds.join(','));
      } else {
        currentUrlParams.delete('ids');
      }
      if (tableId === '#carsTable') {
        const newUrl = window.location.pathname + '?' + currentUrlParams.toString().replace(/&$/, '');
        window.history.replaceState({path: newUrl}, '', newUrl);
      }
    });

    compareBtn.on('click', function () {
      const idsArray = table.find('.' + checkboxClass + ':checked').map(function () {
        return this.value;
      }).get();

      if (idsArray.length > 0) {
        const comparePageUrlParams = new URLSearchParams();
        comparePageUrlParams.set('ids', idsArray.join(','));

        const returnToUrlParams = new URLSearchParams(window.location.search);
        if (idsArray.length > 0) {
          returnToUrlParams.set('ids', idsArray.join(','));
        } else {
          returnToUrlParams.delete('ids');
        }

        comparePageUrlParams.set('return_to', originPageName);
        comparePageUrlParams.set('return_params', returnToUrlParams.toString());

        window.location.href = `/cars/compare?${comparePageUrlParams.toString()}`;
      } else {
        alert('Будь ласка, оберіть автомобілі для порівняння.');
      }
    });

    resetBtn.on('click', function () {
      table.find('.' + checkboxClass).prop('checked', false);
      updateCompareButtonState();
      if (tableId === '#carsTable') {
        const currentUrlParams = new URLSearchParams(window.location.search);
        currentUrlParams.delete('ids');
        const newUrl = window.location.pathname + '?' + currentUrlParams.toString().replace(/&$/, '');
        window.history.replaceState({path: newUrl}, '', newUrl);
      }
    });
  }

  initializeCompareLogic('#carsTable', '#compareBtn', '#resetBtn', 'compare-checkbox', 'history');
  initializeCompareLogic('#searchResultsTable', '#compareBtnSearchPage', '#resetBtnSearchPage', 'compare-checkbox-search', 'search');

  function initializeDeleteModal() {
    const modalElement = document.getElementById('confirmDeleteModal');
    if (!modalElement) return;

    const deleteForm = modalElement.querySelector('#deleteOfferForm');
    const offerDescriptionEl = modalElement.querySelector('#offerDescriptionToDelete');
    const flashContainer = document.getElementById('flash-messages');

    if (!deleteForm || !offerDescriptionEl ) {
      return;
    }

    let currentOfferIdToDelete = null;

    modalElement.addEventListener('show.bs.modal', event => {
      const button = event.relatedTarget;
      currentOfferIdToDelete = button.getAttribute('data-offer-id');
      const description = button.getAttribute('data-offer-description');
      offerDescriptionEl.textContent = description || 'це оголошення';
      deleteForm.action = `/cars/${currentOfferIdToDelete}/delete`;
      deleteForm.dataset.currentOfferId = currentOfferIdToDelete;
    });

    deleteForm.addEventListener('submit', async function(event) {
      event.preventDefault();
      const offerId = this.dataset.currentOfferId;
      if (!offerId) return;
      try {
        const response = await fetch(`/cars/${offerId}/delete`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Server error: ${response.status} ${errorText}`);
        }
        const htmlFlashMessages = await response.text();
        if (flashContainer) {
          flashContainer.innerHTML = htmlFlashMessages;
        } else {
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = htmlFlashMessages;
          const alertMessage = tempDiv.querySelector('.alert')?.textContent || 'Дія виконана.';
          alert(alertMessage.trim());
        }
        let rowToRemove = document.getElementById(`car-row-${offerId}`);
        if (!rowToRemove) {
          rowToRemove = document.getElementById(`car-row-search-${offerId}`);
        }
        if (rowToRemove) rowToRemove.remove();

        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();
      } catch (error) {
        console.error('Помилка під час видалення:', error);
        const errorMessage = `<div class="alert alert-danger alert-dismissible fade show" role="alert">Не вдалося видалити оголошення. Помилка: ${error.message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
        if (flashContainer) flashContainer.innerHTML = errorMessage;
        else alert(`Не вдалося видалити оголошення. ${error.message}`);
      }
    });
  }
  initializeDeleteModal();

  function clearUrlParamsAfterPostAndForFlash() {
    const flashMessagesExist = document.querySelector('.flash-messages-container .alert');
    if (flashMessagesExist && window.location.search) {
    }
    if (document.getElementById('flash-messages') && window.location.pathname.endsWith('/search')) {
    }
  }
  clearUrlParamsAfterPostAndForFlash();

  const dutyFuelSelect = document.getElementById('fuel_type');
  if (dutyFuelSelect) {
    const dutyEngineInput = document.getElementById('engine_volume');
    const dutyBatteryInput = document.getElementById('battery_capacity_kwh');
    function toggleDutyFields() {
      if (!dutyFuelSelect || !dutyEngineInput || !dutyBatteryInput) return;
      if (dutyFuelSelect.value === 'electric') {
        dutyEngineInput.disabled = true; dutyEngineInput.value = '';
        dutyBatteryInput.disabled = false;
      } else {
        dutyEngineInput.disabled = false;
        dutyBatteryInput.disabled = true; dutyBatteryInput.value = '';
      }
    }
    toggleDutyFields();
    dutyFuelSelect.addEventListener('change', toggleDutyFields);

    const dutyForm = document.getElementById('dutyForm');
    if (dutyForm && document.querySelector('#dutyForm + .mt-5 .list-group')) {
    }
  }

});