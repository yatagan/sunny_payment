from starlette.testclient import TestClient

import api

client = TestClient(api.app)


def test_register():
    response = client.post('/register',
                           json={
                               'currency': 'NOT a CURRENCY',
                               'name': 'Dummy',
                               'country': 'USA',
                               'city': 'Boston',
                           })

    assert response.status_code != 200
    assert response.json()['detail'][0]['msg'] == 'Invalid currency'


# transfer
# # negative amount
# with pytest.raises(Exception):
#     transfer_money(session, client1_id, client2_id, -100)
