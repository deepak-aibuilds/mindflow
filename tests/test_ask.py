import pytest
from pydantic import BaseModel
from unittest.mock import patch, AsyncMock
class Question(BaseModel):
    question: str



@pytest.mark.anyio
async def test_ask(client):
    question = Question(question='What is Yeti Growth?')
    with patch(
        'app.services.rag_service.llm',
        new_callable=AsyncMock
    ) as mock_llm:
        mock_llm.ainvoke = AsyncMock()
        mock_llm.ainvoke.return_value.content = "Yetigrowth is good"

        response = await client.post('/ask', json=question.model_dump())
        assert response.status_code == 200
