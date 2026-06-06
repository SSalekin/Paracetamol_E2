import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


for parent in Path(__file__).resolve().parents:
    env_path = parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        break


DOLA_API_KEY = os.getenv("DOLA_API_KEY")
DOLA_BASE_URL = os.getenv(
    "DOLA_BASE_URL",
    "https://ark.cn-beijing.volces.com/api/v3",
)


def get_llm() -> ChatOpenAI:
    if not DOLA_API_KEY:
        raise RuntimeError("DOLA_API_KEY is missing. Add it to your .env file.")

    return ChatOpenAI(
        model="seed-2-0-lite-260428",
        api_key=DOLA_API_KEY,
        base_url=DOLA_BASE_URL,
        temperature=0.1,
    )
