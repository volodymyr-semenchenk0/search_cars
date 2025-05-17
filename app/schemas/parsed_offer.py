from typing import Optional

from pydantic import BaseModel, HttpUrl, Field, validator


class ParsedCarOffer(BaseModel):
    identifier: str = Field(..., description="Унікальний ідентифікатор пропозиції на сайті-джерелі")
    link_to_offer: HttpUrl = Field(..., description="Пряме посилання на пропозицію")
    price: Optional[float] = Field(None, gt=0, description="Ціна автомобіля")
    currency: Optional[str] = Field(None, max_length=3, description="Валюта ціни, наприклад, EUR")
    country_code: Optional[str] = Field(None, description="Код країни оголошення (напр. DE, PL)")
    make: Optional[str] = Field(None, description="Марка автомобіля")
    model: Optional[str] = Field(None, description="Модель автомобіля")
    year: Optional[int] = Field(None, description="Рік виробництва")
    body_type: Optional[str] = Field(None, description="Тип кузова")
    fuel_type: Optional[str] = Field(None, description="Ключ типу пального (напр., 'diesel', 'electric')")
    engine_volume: Optional[int] = Field(None, ge=0, description="Об'єм двигуна в см³")
    battery_capacity_kwh: Optional[float] = Field(None, ge=0, description="Ємність батареї в кВт·год")
    transmission: Optional[str] = Field(None, description="Тип коробки передач")
    drive: Optional[str] = Field(None, description="Тип приводу")
    mileage: Optional[int] = Field(None, ge=0, description="Пробіг в км")

    @validator('make', 'model', 'fuel_type', 'body_type', 'transmission', 'drive', pre=True, always=True)
    def sanitize_string_fields(cls, v):
        if isinstance(v, str):
            return v.strip() if v.strip() else None
        return None
