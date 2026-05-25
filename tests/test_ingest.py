import pytest

@pytest.mark.anyio
async def test_ingest(client):
    response = await client.post('/ingest', data={'source_type': 'xml'})
    assert response.status_code == 400

