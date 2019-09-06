import datetime

from sqlalchemy import and_, or_
from db.mappings import Client, Wallet, CurrencyRate, TransactionLog, TransactionTypeEnum

# FIXME: get some quotes
DEFAULT_EXCHANGE_RATE = 1


def register_client(session, name, country, city, currency):
    client = Client(name=name, country=country, city=city)
    client.wallet = Wallet(currency=currency)

    session.add(client)
    session.commit()

    return {
        'client_id': client.id,
    }


def refill_wallet(session, client_id, amount):
    client = session.query(Client).filter(Client.id == client_id).one()
    client.wallet.balance += amount

    log = TransactionLog(type='refill', wallet_to=client.wallet, amount=amount)
    session.add(log)

    session.commit()
    return {
        'balance': client.wallet.balance,
    }


def get_exchange_rate(session, quote_currency, base_currency, date=datetime.date.today()):
    if base_currency == 'USD':
        currency_rate = session \
            .query(CurrencyRate) \
            .filter(and_(CurrencyRate.currency == quote_currency, CurrencyRate.date == date)) \
            .one_or_none()
        return currency_rate.rate if currency_rate else DEFAULT_EXCHANGE_RATE
    elif quote_currency == 'USD':
        currency_rate = session \
            .query(CurrencyRate) \
            .filter(and_(CurrencyRate.currency == base_currency, CurrencyRate.date == date)) \
            .one_or_none()
        return 1 / currency_rate.rate if currency_rate else DEFAULT_EXCHANGE_RATE
    else:
        return get_exchange_rate(session, quote_currency, 'USD', date) \
               * get_exchange_rate(session, 'USD', base_currency, date)


def transfer_money(session, client_id_from, client_id_to, amount):
    client_from = session.query(Client).filter(Client.id == client_id_from).one()
    client_to = session.query(Client).filter(Client.id == client_id_to).one()

    if amount > client_from.wallet.balance:
        raise Exception('Not enough money')

    is_same_currency = client_from.wallet.currency == client_to.wallet.currency
    if is_same_currency:
        client_from.wallet.balance -= amount
        client_to.wallet.balance += amount

        rate = None
    else:
        rate = get_exchange_rate(session, client_from.wallet.currency, client_to.wallet.currency)
        base_currency_amount = amount * rate

        client_from.wallet.balance -= amount
        client_to.wallet.balance += base_currency_amount

    log = TransactionLog(
        type='transfer',
        wallet_from=client_from.wallet,
        wallet_to=client_to.wallet,
        amount=amount,
        exchange_rate=rate
    )
    session.add(log)

    session.commit()


def add_currency_rate(session, date, currency, rate):
    currency_rate = CurrencyRate(date=date, currency=currency, rate=rate)
    session.add(currency_rate)
    session.commit()


def get_client_transactions(session, client_name, date_from, date_to):
    client = session.query(Client).filter(Client.name == client_name).one_or_none()
    if not client:
        raise Exception('No such client')

    query = session.query(TransactionLog) \
        .filter(or_(TransactionLog.wallet_from == client.wallet, TransactionLog.wallet_to == client.wallet))

    if date_from:
        query = query.filter(date_from <= TransactionLog.datetime)
    if date_to:
        query = query.filter(TransactionLog.datetime <= date_to)

    logs = []
    for t in query.order_by(TransactionLog.datetime).all():
        log = {
            'datetime': t.datetime,
            'type': t.type.name,
            'amount': t.amount
        }
        if t.type == TransactionTypeEnum.transfer:
            log['from'] = t.wallet_from.client.name
            log['to'] = t.wallet_to.client.name
            if t.exchange_rate:
                log['exchange_rate'] = t.exchange_rate

        logs.append(log)

    return logs
