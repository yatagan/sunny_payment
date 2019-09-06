import os
from functools import wraps
import datetime

from fastapi import FastAPI

import db
import core
from validation import ClientInput, RefillInput, TransferInput, CurrencyRateInput

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


@app.get('/report')
@add_status_handle_errors
async def client_transactions_report(
        client_name: str,
        date_from: datetime.date = None,
        date_to: datetime.date = None):
    with db.session_scope() as session:
        return core.get_client_transactions(session, client_name, date_from, date_to)
