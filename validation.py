import decimal
import datetime

from pydantic import BaseModel, validator

CURRENCIES = {'USD', 'EUR', 'CAD', 'CNY'}


def normalize_money(raw):
    cents = decimal.Decimal('0.01')
    return decimal.Decimal(raw).quantize(cents, decimal.ROUND_HALF_UP)


class ClientInput(BaseModel):
    name: str
    country: str
    city: str
    currency: str

    @validator('currency')
    def validate_normalize_currency(cls, currency):
        currency_normal = currency.upper()
        if currency_normal not in CURRENCIES:
            raise ValueError('Invalid currency')
        return currency_normal


class MoneyInput(BaseModel):
    amount: float

    @validator('amount')
    def validate_normalize_money(cls, amount):
        if amount < 0:
            raise ValueError("Transfer amount can't be negative")
        return normalize_money(amount)


class RefillInput(MoneyInput):
    client_id: int


class TransferInput(MoneyInput):
    client_id_from: int
    client_id_to: int

    @validator('client_id_to')
    def check_are_ids_equal(cls, v, values):
        if 'client_id_from' in values and v == values['client_id_from']:
            raise ValueError("Can't transfer to yourself")
        return v


class CurrencyRateInput(BaseModel):
    date: datetime.date = datetime.date.today()
    rate: float
    currency: str

    @validator('currency')
    def validate_normalize_currency_not_usd(cls, currency):
        currency_normal = currency.upper()
        if currency_normal not in CURRENCIES - {'USD'}:
            raise ValueError('Invalid currency')
        return currency_normal

    @validator('rate')
    def validate_rate(cls, rate):
        if rate <= 0:
            raise ValueError('Invalid rate')
        return rate
