from app.customs import CalculateCustoms

price_val = 3500.0
engine_volume = 1500.0
year_val = 2015
fuel_val = "Electric"


customs_uah, final_price = None, None
calc_customs = CalculateCustoms().calculate(
    price_val,
    engine_volume,
    year_val,
    fuel_val
)


print(calc_customs)