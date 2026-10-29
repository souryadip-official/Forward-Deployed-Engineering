from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

def get_response(query: str, api_key: str) -> str:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=api_key
    )

    response = model.invoke(query).content
    return response