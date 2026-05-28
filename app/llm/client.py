from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from app.schemas import DigestOutput, ActionItems


load_dotenv()


def load_prompt(name: str) -> str:
    path = Path(__file__).parent /  f"{name}.txt"
    return path.read_text()


digester= load_prompt('prompts/digest_v1')
digest_prompt= ChatPromptTemplate.from_template(digester)




def get_digest():
    return digest_prompt | llm.with_structured_output(DigestOutput)


action_extractor = load_prompt('prompts/action_v1')
action_prompt = ChatPromptTemplate.from_template(action_extractor)

primary_llm  = ChatMistralAI(model="mistral-small-latest")
fallback_llm = ChatGroq(model="llama-3.3-70b-versatile")

# LangChain built-in fallback
llm = primary_llm.with_fallbacks([fallback_llm])


def get_actionitem():
    return action_prompt | llm.with_structured_output(ActionItems)