from unittest.mock import patch, MagicMock
from langchain_mistralai import MistralAIEmbeddings

async def test_search_mocked(client):
    with patch.object(MistralAIEmbeddings, "embed_query", return_value=[0.1] * 1024):
        with patch("app.services.search_service.co.rerank") as mock_rerank:
            mock_rerank.return_value = MagicMock(results=[])
            
            response = await client.get('/search', params={'q': 'test', 'limit': 3})
            assert response.status_code == 200