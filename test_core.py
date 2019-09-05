import pytest

import db

from db.mappings import Client, Wallet
from core import register_client, refill, transfer

db.init('sqlite://')


def test_register():
    client_info = {
        'name': 'Dummy',
        'country': 'USA',
        'city': 'Boston',
        'currency': 'USD',
    }
    with db.session_scope() as session0:
        response = register_client(session0, **client_info)
        client_id = response['client_id']

    with db.session_scope() as session1:
        client = session1.query(Client).filter(Client.id == client_id).one()
        for key in 'name', 'country', 'city':
            assert client_info.get(key) == getattr(client, key)
        assert client.wallet.currency == client_info['currency']


def test_refill():
    with db.session_scope() as session:
        resp = register_client(session, 'Dan', 'Κυπριακή Δημοκρατία', 'Λευκωσία', 'EUR')
        client_id = resp['client_id']
        init_balance = 777
        refill(session, client_id, init_balance)

    with db.session_scope() as session:
        wallet = session.query(Wallet).filter(Wallet.client_id == client_id).one()
        assert wallet.balance == init_balance

        more_money = 666
        refill(session, client_id, more_money)

    with db.session_scope() as session:
        wallet = session.query(Wallet).filter(Wallet.client_id == client_id).one()
        assert wallet.balance == init_balance + more_money


def test_transfer():
    with db.session_scope() as session:
        resp1 = register_client(session, 'Vasa', 'France', 'Paris', 'CNY')
        resp2 = register_client(session, 'Valera', 'Germany', 'Berlin', 'CNY')
        resp3 = register_client(session, 'Masha', 'US', 'Boston', 'USD')

        client1_id = resp1['client_id']
        client2_id = resp2['client_id']
        client3_id = resp3['client_id']

        refill(session, client1_id, 111)
        refill(session, client2_id, 222)
        refill(session, client3_id, 333)

    # equal currency transfer
    with db.session_scope() as session:
        transfer(session, client1_id, client2_id, 100)

    with db.session_scope() as session:
        client1 = session.query(Client).filter(Client.id == client1_id).one()
        client2 = session.query(Client).filter(Client.id == client2_id).one()
        assert client1.wallet.balance == 11
        assert client2.wallet.balance == 322

        # negative amount
        with pytest.raises(Exception):
            transfer(session, client1_id, client2_id, -100)

        # not enough money
        with pytest.raises(Exception):
            transfer(session, client1_id, client2_id, 12)

    # cross-currency transfer
    with db.session_scope() as session:
        with pytest.raises(Exception):
            transfer(session, client2_id, client3_id, 10)

    with db.session_scope() as session:
        pass
