from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    """
    Simple endpoint to handle chat between user and ChatGPT.
    For now, just return the message and the command.
    """
    data = request.json
    user_message = data.get("message", "")  # Get the user's message
    chat_history = data.get("chatHistory", "")  # Get the current chat history

    # For debugging, returning the user message and what the command would be.
    command = f"Sending to ChatGPT: {chat_history + '\nUser: ' + user_message}"

    return jsonify({
        "reply": f"Received your message: {user_message}",
        "command": command,
        "status": "ChatGPT command constructed."
    })

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    """
    A simple endpoint to confirm button clicks.
    """
    return jsonify({
        "status": "fetch_schema button clicked, but nothing to fetch."
    })

@app.route("/kpi_query", methods=["POST"])
def kpi_query():
    """
    Simple confirmation for KPI query button click.
    """
    return jsonify({
        "status": "KPI query button clicked, but no SQL executed."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
