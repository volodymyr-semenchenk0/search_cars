import requests
import json
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_all_makes():
    """
    Повертає список усіх автомобільних марок з CarQuery API (JSONP) з кешуванням.
    """
    try:
        response = requests.get(
            'https://www.carqueryapi.com/api/0.3/?cmd=getMakes&callback=cb',
            headers={'User-Agent': 'Mozilla/5.0'}, timeout=5
        )
        text = response.text
        start = text.find('(')
        end = text.rfind(')')
        if start < 0 or end < 0:
            logger.error(f"Invalid JSONP for makes: {text[:100]}")
            return []
        payload = text[start+1:end]
        data = json.loads(payload)
        return data.get('Makes', [])
    except Exception as e:
        logger.error(f"Error fetching makes: {e}")
        return []

@lru_cache(maxsize=128)
def get_models_for_make(make_id):
    """
    Повертає список усіх унікальних моделей для make_id
    з CarQuery API через виклик GetTrims (JSONP) з кешуванням.
    """
    try:
        url = f'https://www.carqueryapi.com/api/0.3/?cmd=getTrims&make={make_id}&callback=cb'
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        text = response.text
        start = text.find('(')
        end = text.rfind(')')
        if start < 0 or end < 0:
            logger.error(f"Invalid JSONP for trims ({make_id}): {text[:100]}")
            return []
        payload = text[start+1:end]
        data = json.loads(payload)
        trims = data.get('Trims', [])
        seen = set()
        models = []
        for t in trims:
            name = t.get('model_name')
            if name and name not in seen:
                seen.add(name)
                models.append({'model_name': name})
        return models
    except Exception as e:
        logger.error(f"Error fetching trims for {make_id}: {e}")
        return []