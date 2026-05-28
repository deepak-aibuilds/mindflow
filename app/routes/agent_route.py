from fastapi import APIRouter, Form
from app.llm import build_graph

router = APIRouter(prefix='/agent', tags=['Agents'])

@router.post('/ask')
async def ask_agent(
    question:str = Form(...)
):
    graph = build_graph()
    result = await graph.ainvoke({
        'query': question,
        'context_required': 'no',
        'response': '',
        'search_results': [],
    })
    return {'answer': result['response']}
