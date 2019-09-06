import decimal

from db.mappings import Client, Wallet, CurrencyRate, TransactionLog


CURRENCIES = {'USD', 'EUR', 'CAD', 'CNY'}


def normalize_money(raw):
    cents = decimal.Decimal('0.01')
    return decimal.Decimal(raw).quantize(cents, decimal.ROUND_HALF_UP)


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


def transfer_money(session, client_id_from, client_id_to, amount):
    client_from = session.query(Client).filter(Client.id == client_id_from).one()
    client_to = session.query(Client).filter(Client.id == client_id_to).one()

    is_same_currency = client_from.wallet.currency == client_to.wallet.currency

    if is_same_currency:
        if amount > client_from.wallet.balance:
            raise Exception('Not enough money')

        client_from.wallet.balance -= amount
        client_to.wallet.balance += amount

        log = TransactionLog(
            type='transfer',
            wallet_from=client_from.wallet,
            wallet_to=client_to.wallet,
            amount=amount
        )
        session.add(log)

        session.commit()
    else:
        pass


def add_currency_rate(session, date, currency, rate):
    currency_rate = CurrencyRate(date=date, currency=currency, rate=rate)
    session.add(currency_rate)
    session.commit()
