from flask import Flask, request
from services.llm_service import get_response
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import json

app = Flask(__name__)

past_messages = [SystemMessage("""
    You are a chat assistant of a support ticket
    resolution app. Please do not respond to any questions
    that are not related to solving general query about ticket resolution,
    refund query, order tracking status, or company policy query.

    If the user asks any question, off topic, then please respond that
    you are not aware of the answer.
""")]

@app.route("/chat", methods=["POST"])
def handle_chat():
    query_json = request.get_json()
    curr_query = query_json.get("query")
    api_key = query_json.get("api_key")

    formed_query: str = ""
    for msg in past_messages:
        q: str = f"{msg}\n"
        formed_query += q

    formed_query = formed_query + f"Now answer: {curr_query}"
    past_messages.append(HumanMessage(curr_query))

    response: str = get_response(formed_query, api_key)
    past_messages.append(AIMessage(response))
    return json.dumps({
        "content": response
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45000, debug=True)