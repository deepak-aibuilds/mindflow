import pytest

@pytest.mark.anyio
async def test_agent(client):
    response = await client.post('/agent/ask', data={'question': "What is YetiGrowth"})
    print(response.json())
    assert response.status_code == 400
    assert response.json()