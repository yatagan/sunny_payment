import os
from functools import wraps
import datetime

from fastapi import FastAPI
from pydantic import BaseModel, validator

import db
import core

db.init(os.getenv('SQL_ENGINE_URI', 'postgresql://postgres:@localhost/sunny_payment'))

app = FastAPI()


def add_status_handle_errors(fun):
    @wraps(fun)
    async def wrapper(*args, **kwargs):
        try:
            return {
                'status': 'ok',
                'data': await fun(*args, **kwargs),
            }
        except Exception as e:
            return {
                'status': 'error',
                'fun': fun.__qualname__,
                'args': (args, kwargs),
                'msg': str(e),
            }
    return wrapper


class ClientInput(BaseModel):
    name: str
    country: str
    city: str
    currency: str

    @validator('currency')
    def validate_normalize_currency(cls, currency):
        currency_normal = currency.upper()
        if currency_normal not in core.CURRENCIES:
            raise ValueError('Invalid currency')
        return currency_normal


class MoneyInput(BaseModel):
    amount: float

    @validator('amount')
    def validate_normalize_money(cls, amount):
        if amount < 0:
            raise ValueError("Transfer amount can't be negative")
        return core.normalize_money(amount)


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
        if currency_normal not in core.CURRENCIES - {'USD'}:
            raise ValueError('Invalid currency')
        return currency_normal

    @validator('rate')
    def validate_rate(cls, rate):
        if rate <= 0:
            raise ValueError('Invalid rate')
        return rate


@app.post('/register')
@add_status_handle_errors
async def register_client(data: ClientInput):
    with db.session_scope() as session:
        return core.register_client(session, data.name, data.country, data.city, data.currency)


@app.put('/refill')
@add_status_handle_errors
async def refill_wallet(data: RefillInput):
    with db.session_scope() as session:
        return core.refill_wallet(session, data.client_id, data.amount)


@app.put('/transfer')
@add_status_handle_errors
async def transfer_money(data: TransferInput):
    with db.session_scope() as session:
        return core.transfer_money(session, data.client_id_from, data.client_id_to, data.amount)


@app.post('/currency_rate')
@add_status_handle_errors
async def add_currency_rate(data: CurrencyRateInput):
    with db.session_scope() as session:
        return core.add_currency_rate(session, data.date, data.currency, data.rate)

