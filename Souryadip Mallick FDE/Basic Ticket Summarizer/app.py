from flask import Flask, request
from services.ticket_summarizer import summarize

app = Flask(__name__)

@app.route("/api/summarize", methods=["POST"])
def handle_summarize():
    data = request.get_json()
    query = str(data.get("query"))
    api_key = str(data.get("api_key"))

    return summarize(query, api_key)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=45000, debug=True)