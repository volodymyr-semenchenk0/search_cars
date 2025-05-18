from app.services import CarMakeService, CarModelService
from app.utils.logger_config import logger


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
    normalized_filters['cy'] = _clean_and_convert(raw_form_data.get('cy'))
    normalized_filters['fuel'] = _clean_and_convert(raw_form_data.get('fuel'), lower=True)

    return normalized_filters
