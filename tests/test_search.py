from unittest.mock import patch, MagicMock
from langchain_mistralai import MistralAIEmbeddings

async def test_search_mocked(client):
    with patch("app.routes.query_routes.search_items") as mock_search:
        mock_search.return_value = [
            {
                "chunk_content": "YetiGrowth is a digital agency",
                "item_title": "YetiGrowth",
                "source_type": "url",
                "item_id": 1
            }
        ]
        response = await client.get('/search', params={'q': 'test', 'limit': 3})
        assert response.status_code == 200