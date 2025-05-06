import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Type

# --- Utility data structures for website configuration ---
@dataclass
class ParamMapping:
    # internal name used in code
    name: str
    # query parameter key expected by the target site
    query_key: str
    # optional formatter to convert value to string
    formatter: Callable[[Any], str] = lambda x: str(x)

@dataclass
class WebsiteConfig:
    key: str
    base_url: str
    search_path: str
    parser_cls: Type
    default_params: Dict[str, str] = field(default_factory=dict)
    param_mappings: List[ParamMapping] = field(default_factory=list)

    def build_search_url(self, **kwargs) -> str:
        # start from defaults
        params = dict(self.default_params)
        # override with provided, using mappings
        for m in self.param_mappings:
            val = kwargs.get(m.name)
            if val not in (None, '', []):
                params[m.query_key] = m.formatter(val)
        # assemble query string
        query = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url.rstrip('/')}{self.search_path}?{query}"

# --- Static option lists ---
current_year = datetime.now().year
years = list(range(1990, current_year + 1))

price_options = [
    500,1000,1500,2000,2500,3000,4000,5000,
    6000,7000,8000,9000,10000,12500,15000,
    17500,20000,25000,30000,40000,50000,
    75000,100000
]

mileage_options = [
    2500,5000,10000,20000,30000,40000,50000,
    60000,70000,80000,90000,100000,125000,
    150000,175000,200000
]

# --- Engine and fuel type definitions ---
ENGINE_TYPES = {
    "Gasoline":     {"label": "Бензин", "code": "GAS"},
    "Diesel":       {"label": "Дизель", "code": "DSL"},
    "Electric":     {"label": "Електро", "code": "ELE"},
    "Electric/Gasoline": {"label": "Гібрид", "code": "HEV"},
    "Electric/Diesel":   {"label": "Плагін-гібрид", "code": "PHEV"},
    "LPG":          {"label": "Газ (LPG)", "code": "LPG"},
    "Ethanol":      {"label": "Газ (Етанол)", "code": "ETH"},
    "CNG":          {"label": "Газ (CNG)", "code": "CNG"},
    "Hydrogen":     {"label": "Водень", "code": "H2"},
    "Others":       {"label": "Інше", "code": "OTH"}
}

FUEL_TYPES = {
    "gasoline":          {"label": "Бензин", "code": "B"},
    "diesel":            {"label": "Дизель", "code": "D"},
    "electric":          {"label": "Електро", "code": "E"},
    "electric/gasoline": {"label": "Електро/Бензин", "code": "2"},
    "electric/diesel":   {"label": "Електро/Дизель", "code": "3"},
    "lpg":               {"label": "Газ (LPG)", "code": "L"},
    "ethanol":           {"label": "Газ (Етанол)", "code": "M"},
    "cng":               {"label": "Газ (Метан)", "code": "C"},
    "hydrogen":          {"label": "Водень", "code": "H"}
}

# --- Website parser configurations ---
from .parsers.autoscout24_parser import AutoScout24Parser

PARSE_WEBSITES: Dict[str, WebsiteConfig] = {
    "autoscout24": WebsiteConfig(
        key="autoscout24",
        base_url="https://www.autoscout24.com",
        search_path="/lst",
        parser_cls=AutoScout24Parser,
        default_params={
            "atype": "C",
            "damaged_listing": "exclude",
            "desc": "0",
            "powertype": "kw",
            "size": "20",
            "sort": "standard",
            "source": "detailpage_back-to-list",
            "ustate": "N,U"
        },
        param_mappings=[
            ParamMapping("brand", "brand"),
            ParamMapping("model", "model"),
            ParamMapping("pricefrom", "pricefrom"),
            ParamMapping("priceto", "priceto"),
            ParamMapping("fregfrom", "fregfrom"),
            ParamMapping("fregto", "fregto"),
            ParamMapping("kmfrom", "kmfrom"),
            ParamMapping("kmto", "kmto"),
            ParamMapping("cy", "cy"),
            ParamMapping("fuel", "fuel")
        ]
    )
}
