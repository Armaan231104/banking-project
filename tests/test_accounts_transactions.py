def _register_and_login(client, email='a@a.com'):
    client.post('/api/v1/auth/register', json={'email': email, 'full_name': 'A', 'password': 'Password123!'})
    return client.post('/api/v1/auth/login', json={'email': email, 'password': 'Password123!'}).json()


def test_account_and_transactions(client):
    tokens = _register_and_login(client)
    h = {'Authorization': f"Bearer {tokens['access_token']}"}

    created = client.post('/api/v1/accounts/', json={'currency': 'USD'}, headers=h)
    assert created.status_code == 200
    acct = created.json()['account_id']

    dep = client.post('/api/v1/transactions/deposit', json={'account_id': acct, 'amount': 100, 'currency': 'USD', 'idempotency_key': 'dep-1'}, headers=h)
    assert dep.status_code == 200
    dep2 = client.post('/api/v1/transactions/deposit', json={'account_id': acct, 'amount': 100, 'currency': 'USD', 'idempotency_key': 'dep-1'}, headers=h)
    assert dep2.json()['id'] == dep.json()['id']

    wd = client.post('/api/v1/transactions/withdraw', json={'account_id': acct, 'amount': 10, 'currency': 'USD'}, headers=h)
    assert wd.status_code == 200

    other = _register_and_login(client, 'b@b.com')
    h2 = {'Authorization': f"Bearer {other['access_token']}"}
    dst = client.post('/api/v1/accounts/', json={'currency': 'USD'}, headers=h2).json()['account_id']

    tr = client.post('/api/v1/transactions/transfer', json={'source_account_id': acct, 'destination_account_id': dst, 'amount': 25, 'currency': 'USD'}, headers=h)
    assert tr.status_code == 200


def test_admin_check(client):
    tokens = _register_and_login(client, 'admin@a.com')
    h = {'Authorization': f"Bearer {tokens['access_token']}"}
    resp = client.get('/api/v1/users/admin-check', headers=h)
    assert resp.status_code == 403
