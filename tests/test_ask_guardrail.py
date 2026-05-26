import pytest
from pydantic import BaseModel
from unittest.mock import patch, AsyncMock
class Question(BaseModel):
    question: str



@pytest.mark.anyio
async def test_ask(client):
    question = Question(question='What is Yeti Growth?')

    with patch('app.services.rag_service.search_items') as mock_search:
        with patch(
            'app.services.rag_service.llm',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_search.return_value = [ ]
            mock_llm.ainvoke = AsyncMock()
            mock_llm.ainvoke.return_value.content = "What is the capital of france?"

            response = await client.post('/ask', json=question.model_dump())
            print(response.json())
            assert response.status_code == 200
            assert 'answer' in response.json()