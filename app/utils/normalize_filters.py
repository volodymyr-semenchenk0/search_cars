from app.repositories import FuelTypeRepository
from app.services import CarMakeService, CarModelService
from app.utils.logger_config import logger
from app.repositories import CountryRepository


def normalize_filters(raw_form_data: dict) -> dict:
    normalized_filters = {}

    make_id_str = raw_form_data.get('make')
    model_id_str = raw_form_data.get('model')

    make_name_for_parser = None
    model_name_for_parser = None

    if make_id_str and make_id_str.strip().isdigit():
        try:
            make_id_int = int(make_id_str.strip())
            make_name = CarMakeService.get_make_name_by_id(make_id_int)
            if make_name:
                make_name_for_parser = make_name.strip().lower().replace(" ", "-")
        except ValueError:
            logger.warning(f"Invalid Make ID format: {make_id_str}")
        except Exception as e:
            logger.error(f"Error fetching make name for ID {make_id_str}: {e}")

    if model_id_str and model_id_str.strip().isdigit() and make_name_for_parser:
        try:
            model_id_int = int(model_id_str.strip())
            model_name = CarModelService.get_model_name_by_id(model_id_int)
            if model_name:
                model_name_for_parser = model_name.strip().lower().replace(" ", "-")
        except ValueError:
            logger.warning(f"Invalid Model ID format: {model_id_str}")
        except Exception as e:
            logger.error(f"Error fetching model name for ID {model_id_str}: {e}")

    normalized_filters['make'] = make_name_for_parser
    normalized_filters['model'] = model_name_for_parser

    def _clean_and_convert(value_str, convert_to_int=False, lower=False, dashify_if_string=False):
        if value_str is None:
            return None

        cleaned_str = str(value_str).strip()

        if not cleaned_str:
            return None

        if convert_to_int:
            try:
                return int(cleaned_str)
            except ValueError:
                logger.warning(f"Could not convert '{cleaned_str}' to int.")
                return None
        else:
            if lower:
                cleaned_str = cleaned_str.lower()
            if dashify_if_string:
                cleaned_str = cleaned_str.replace(" ", "-")
            return cleaned_str

    normalized_filters['pricefrom'] = _clean_and_convert(raw_form_data.get('pricefrom'), convert_to_int=True)
    normalized_filters['priceto'] = _clean_and_convert(raw_form_data.get('priceto'), convert_to_int=True)
    normalized_filters['fregfrom'] = _clean_and_convert(raw_form_data.get('fregfrom'), convert_to_int=True)
    normalized_filters['fregto'] = _clean_and_convert(raw_form_data.get('fregto'), convert_to_int=True)
    normalized_filters['kmfrom'] = _clean_and_convert(raw_form_data.get('kmfrom'), convert_to_int=True)
    normalized_filters['kmto'] = _clean_and_convert(raw_form_data.get('kmto'), convert_to_int=True)

    raw_cy_iso_code_from_form = _clean_and_convert(raw_form_data.get('cy'))

    if raw_cy_iso_code_from_form:
        parsing_code = CountryRepository.get_parsing_code_by_iso_code(raw_cy_iso_code_from_form)
        normalized_filters['cy'] = parsing_code if parsing_code else None
        logger.info(f"Normalized 'cy': from ISO '{raw_cy_iso_code_from_form}' to parser code '{normalized_filters['cy']}'")
    else:
        normalized_filters['cy'] = None


    normalized_filters['fuel'] = _clean_and_convert(raw_form_data.get('fuel'), lower=True)

    raw_fuel_key_name = raw_form_data.get('fuel')
    fuel_code_for_parser = None

    if raw_fuel_key_name and isinstance(raw_fuel_key_name, str) and raw_fuel_key_name.strip():
        cleaned_fuel_key_name = raw_fuel_key_name.strip().lower()
        try:
            fuel_code_for_parser = FuelTypeRepository.get_code_by_key_name(cleaned_fuel_key_name)
            if not fuel_code_for_parser:
                logger.warning(f"Не знайдено код для типу пального з ключем: '{cleaned_fuel_key_name}'")
        except Exception as e:
            logger.error(f"Помилка при отриманні коду типу пального для '{cleaned_fuel_key_name}': {e}")

    normalized_filters['fuel'] = fuel_code_for_parser

    return normalized_filters
