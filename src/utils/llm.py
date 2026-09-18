import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set, check your .env file")
        _llm = ChatGroq(model=MODEL_NAME, temperature=0.2, api_key=api_key)
    return _llm
