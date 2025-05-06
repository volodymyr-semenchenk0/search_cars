$(function(){
    // Select2 initialization for brand/model
    $("#make").select2({ theme:'bootstrap-5', placeholder:'Оберіть марку', allowClear:true, width:'100%' });
    $("#model").select2({ theme:'bootstrap-5', placeholder:'Оберіть модель', allowClear:true, width:'100%' });

    // Load models on brand change
    $('#make').on('change', function() {
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
            modelSelect.html(opts)
              .prop('disabled', false)
              .trigger('modelsLoaded');  // ← ось тут
        });
    });



    // Button enable/disable logic
    const $form = $('#searchForm'), $btn = $('#searchBtn');
    const init = {
        make:     $('#make').val(),
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

  // Після завантаження моделей, відновлюємо вибрану модель
  const initialModel = $('#model').data('initial-model');
  if (initialModel) {
    // Запускаємо change на бренд, щоб підвантажити моделі
    $('#brand').trigger('change');
    $('#model').on('modelsLoaded', function () {
      $(this).val(initialModel).trigger('change');
    });
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