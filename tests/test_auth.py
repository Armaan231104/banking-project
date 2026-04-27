def test_auth_flow(client):
    reg = client.post('/api/v1/auth/register', json={'email': 'u@example.com', 'full_name': 'User', 'password': 'Password123!'})
    assert reg.status_code == 200

    login = client.post('/api/v1/auth/login', json={'email': 'u@example.com', 'password': 'Password123!'})
    assert login.status_code == 200
    tokens = login.json()

    me = client.get('/api/v1/users/me', headers={'Authorization': f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200

    refreshed = client.post('/api/v1/auth/refresh', json={'refresh_token': tokens['refresh_token']})
    assert refreshed.status_code == 200
    second = refreshed.json()

    reused = client.post('/api/v1/auth/refresh', json={'refresh_token': tokens['refresh_token']})
    assert reused.status_code == 401

    logout = client.post('/api/v1/auth/logout', json={'refresh_token': second['refresh_token']})
    assert logout.status_code == 200
