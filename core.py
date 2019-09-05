import decimal

from db.mappings import Client, Wallet


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


def refill(session, client_id, amount):
    if amount < 0:
        raise ValueError("Amount can't be negative")

    client = session.query(Client).filter(Client.id == client_id).one()
    client.wallet.balance += amount
    session.commit()
    return {
        'balance': client.wallet.balance,
    }


def transfer(session, client_id_from, client_id_to, amount):
    if amount < 0:
        raise ValueError("Amount can't be negative")

    client_from = session.query(Client).filter(Client.id == client_id_from).one()
    client_to = session.query(Client).filter(Client.id == client_id_to).one()

    is_same_currency = client_from.wallet.currency == client_to.wallet.currency

    if is_same_currency:
        if amount > client_from.wallet.balance:
            raise Exception('Not enough money')

        client_from.wallet.balance -= amount
        client_to.wallet.balance += amount
        session.commit()
    else:
        raise Exception('implement exchange')

