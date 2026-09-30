from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()


def get_llm():

    llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0
    )

    return llm