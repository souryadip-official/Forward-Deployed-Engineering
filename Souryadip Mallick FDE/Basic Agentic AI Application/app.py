import os

from flask import Flask, request, jsonify, render_template
from services.llm_service import get_response
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

app = Flask(__name__)

SYSTEM_PROMPT = SystemMessage("""
    You are a helpful AI assistant with access to external tools.

    Follow these rules:
    - For arithmetic calculations, ALWAYS use the invoke_calculate tool.
    - Always use invoke_calculate tool for even trivial calculation
    - For current weather, ALWAYS use the invoke_weather tool.
    - For currency conversion or exchange rates, ALWAYS use the invoke_exchange_rate tool.
    - You may call multiple tools when solving a multi-step request.
    - After receiving tool results, explain the answer naturally.
    - Never invent current weather or exchange-rate information.
""")

past_messages = [SYSTEM_PROMPT]
msg_counter = 0


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def handle_chat():
    global msg_counter
    query_json = request.get_json()
    curr_query = query_json.get("query")
    api_key = query_json.get("api_key") or os.getenv("GOOGLE_API_KEY")

    if not curr_query:
        return jsonify({
            "error": "Query is required"
            }), 400

    if not api_key:
            return jsonify({
                "error": "Add your Gemini API key in the settings panel or GOOGLE_API_KEY environment variable."
            }), 400

    formed_query: str = ""
    msg_counter += 1

    if msg_counter > 10:
        # Conversation history
        for msg in past_messages:
            q: str = f"{msg}\n"
            formed_query += q

        msg_counter = 0
        
        # invoke summarization
        formed_query += """
            Summarize the conversation with losing important information.
            Keep the summary concise and useful for future responses.
        """

        summarized_context = get_response(formed_query, api_key)["content"]
        
        past_messages.clear()
        past_messages.append(SYSTEM_PROMPT)
        past_messages.append(HumanMessage(f"Summary of previous conversation:\n{summarized_context}"))

        formed_query: str = ""
        for msg in past_messages:
            q: str = f"{msg}\n"
            formed_query += q

        formed_query += f"\nNow answer: {curr_query}"
        past_messages.append(HumanMessage(curr_query))
        
        msg_counter = 1 # Current query is stored in the past_messages
    
    else:
        for msg in past_messages:
            q: str = f"{msg}\n"
            formed_query += q

        formed_query = formed_query + f"Now answer: {curr_query}"
        past_messages.append(HumanMessage(curr_query))

    response = get_response(formed_query, api_key)
    print(f"Tools invoked: {response['tool_calls']}")
    past_messages.append(AIMessage(response["content"]))
    return jsonify({
        "content": response["content"],
        "tool_calls": response["tool_calls"],
        "tool_results": response["tool_results"]
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45000, debug=True)