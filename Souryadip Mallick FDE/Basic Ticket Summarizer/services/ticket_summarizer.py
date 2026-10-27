import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

def summarize(ticket: str, api_key:str) -> str:
    # Initialising the client
    client = Client(
        api_key=api_key
    )

    # Generating response
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Summarize the ticket in 2 lines:\n{ticket}"
    )

    return response.text