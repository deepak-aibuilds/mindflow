from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from .client import llm, load_prompt
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.db import engine
from langgraph.graph import StateGraph, END
from app.services import search_items


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class AgentState(TypedDict):
    query:            str
    context_required: Literal['yes', 'no']
    search_results:   list
    response:         str

class context_required(BaseModel):
    context_required: Literal['yes', 'no']

class llm_response(BaseModel):
    response: str

async def decide_node(state:AgentState) -> dict:
    '''This tool decides whether the llm requires more context
    to answer that question or not'''
    query = state['query']
    prompt_txt = load_prompt('prompts/decider_v1')
    prompt = ChatPromptTemplate.from_template(prompt_txt)
    decider_llm = prompt | llm.with_structured_output(context_required)
    response = await decider_llm.ainvoke({
        'query': query
    })
    return {"context_required": response.context_required}

async def search_node(state:AgentState) -> dict:
    'This tool searches the db for similar chuncks related to the query'
    async with AsyncSessionLocal() as db:
        results = await search_items(state['query'], 5, db)
    return {'search_results': results}

async def answer_node(state:AgentState) -> dict:
    '''this tool uses llm to answer query based on agent state'''
    answer_query = state['query']
    prompt_txt = load_prompt('prompts/answer_v1')
    prompt = ChatPromptTemplate.from_template(prompt_txt)
    answer_llm = prompt | llm.with_structured_output(llm_response)
    if state['context_required'] == 'yes':
        context_str = '\n'.join([res['chunk_content'] for res in state['search_results']])
        
    else:
        context_str = 'There Is No Context Available. Answer Accordingly'
    response = await answer_llm.ainvoke({
            'query': answer_query,
            'context': context_str
            
        })
    return {'response': response.response}

def build_graph():
    graph = StateGraph(AgentState)
    # Add nodes
    graph.add_node("decide", decide_node)
    graph.add_node("search", search_node)
    graph.add_node("answer", answer_node)
    graph.set_entry_point("decide")
    graph.add_conditional_edges(
    "decide",
    lambda state: "search" if state["context_required"] == "yes" else "answer",
    {
        "search": "search",
        "answer": "answer"
    }
    )
    graph.add_edge("search", "answer")
    
    # After answer — end
    graph.add_edge("answer", END)
    
    return graph.compile()






