from datetime import datetime as dt

def get_seasonal_discount(month):
    """Возвращает процент скидки в зависимости от месяца."""
    # Лето (6,7,8) -> распродажа в августе (8)
    if month == 8: return 20
    # Зима (12, 1, 2) -> распродажа в феврале (2)
    if month == 2: return 20
    # Демисезон (3,4,5, 9,10,11) -> распродажа в мае (5) и ноябре (11)
    if month in [5, 11]: return 20
    
    return 0

def calculate_final_price(price, model_discount, current_month=None):
    """Считает итоговую цену с учетом скидки модели и сезона."""
    if current_month is None:
        current_month = dt.now().month
    
    season_disc = get_seasonal_discount(current_month)
    
    # Формула: цена * (1 - скидка_модели/100) * (1 - скидка_сезона/100)
    final_price = price * (1 - model_discount / 100) * (1 - season_disc / 100)
    
    return round(final_price, 2)