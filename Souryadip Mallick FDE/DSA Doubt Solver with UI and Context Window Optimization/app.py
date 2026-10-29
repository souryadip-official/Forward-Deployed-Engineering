from flask import Flask, request, jsonify, render_template
from services.llm_service import get_response
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

app = Flask(__name__)

SYSTEM_PROMPT = SystemMessage("""
    You are an expert doubt solver of DSA subject of Computer Science.

    You are expected to solve any DSA question asked to you
    by the user in a friendly and easy way without letting the
    user get bored and trying to engage them in the conversation.

    Your behavior should be friendly and supporting.

    Do not respond to any question other than DSA. 
    No other topic, not even any other subject even if related to Computer Science.
    If asked anything off-topic, answer that you have no knowledge of that.
""")

past_messages = [SYSTEM_PROMPT]
msg_counter = 0


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reset", methods=["POST"])
def reset_conversation():
    global past_messages, msg_counter
    past_messages = [SYSTEM_PROMPT]
    msg_counter = 0
    return jsonify({"status": "reset"}), 200


@app.route("/chat", methods=["POST"])
def handle_chat():
    global msg_counter
    query_json = request.get_json()
    curr_query = query_json.get("query")
    api_key = query_json.get("api_key")

    if not curr_query:
        return jsonify({
            "error": "Query is required"
            }), 400

    formed_query: str = ""

    msg_counter += 1

    if msg_counter > 20:
        # Conversation history
        for msg in past_messages:
            q: str = f"{msg}\n"
            formed_query += q

        msg_counter = 0
        
        # invoke summarization
        formed_query += """
            Summarize the conversation above, preserving:
            1. Important DSA concepts discussed
            2. Problems and their solutions
            3. User preferences and learning progress
            4. Unresolved doubts and relevant context

            Keep the summary concise and useful for future responses.
        """

        summarized_context = get_response(formed_query, api_key)
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

    response: str = get_response(formed_query, api_key)
    past_messages.append(AIMessage(response))
    return jsonify({
        "content": response
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45000, debug=True)