from flask import Flask, request
from services.llm_service import get_response
import json

app = Flask(__name__)

class Message:
    by: str
    content: str

    def __init__(self, by, content):
        self.by = by
        self.content = content

past_messages = []

@app.route("/chat", methods=["POST"])
def handle_chat():
    query_json = request.get_json()
    curr_query = query_json.get("query")
    api_key = query_json.get("api_key")

    formed_query: str = ""
    for msg in past_messages:
        q = f"{msg.by}: {msg.content}\n"
        formed_query += q

    formed_query = formed_query + f"Now answer: {curr_query}"
    past_messages.append(Message("user", curr_query))

    response = get_response(formed_query, api_key)
    past_messages.append(Message("chat_assistant", response))
    return json.dumps({
        "content": response
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45000, debug=True)