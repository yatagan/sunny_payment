import os
from functools import wraps

from fastapi import FastAPI

import db
import core

db.init(os.getenv('SQL_ENGINE_URI', 'postgresql://postgres:@localhost/sunny_payment'))

app = FastAPI()


def with_status(fun):
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
@with_status
async def register(name, country, city, currency):
    with db.session_scope() as session:
        return core.register_client(session, name, country, city, currency)


@app.put('/refill')
@with_status
async def refill(client_id, amount):
    with db.session_scope() as session:
        amount = core.normalize_money(amount)
        return core.refill(session, client_id, amount)


@app.put('/transfer')
@with_status
async def transfer(client_id_from, client_id_to, amount):
    with db.session_scope() as session:
        amount = core.normalize_money(amount)
        return core.transfer(session, client_id_from, client_id_to, amount)
