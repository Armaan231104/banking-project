def test_statement_export_unconfigured_s3(client):
    client.post('/api/v1/auth/register', json={'email': 's3@a.com', 'full_name': 'A', 'password': 'Password123!'})
    tokens = client.post('/api/v1/auth/login', json={'email': 's3@a.com', 'password': 'Password123!'}).json()
    h = {'Authorization': f"Bearer {tokens['access_token']}"}
    acct = client.post('/api/v1/accounts/', json={'currency': 'USD'}, headers=h).json()['account_id']
    resp = client.post(f'/api/v1/accounts/{acct}/statements/export', headers=h)
    assert resp.status_code == 503
