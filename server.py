import logging
from flask import Flask, request, jsonify
import openai
import os

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)

# OpenAI API Key (must be set as an environment variable on Fly.io)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    """
    Simple endpoint to echo the user message and simulate sending to ChatGPT.
    """
    logging.debug("Received a request at '/chat' endpoint")
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")
    full_message = chat_history + "\nUser: " + user_message
    logging.debug(f"Full message: {full_message[:200]}...")  # log first 200 characters

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_message}]
        )
        reply = response["choices"][0]["message"]["content"]
        logging.debug("Received response from OpenAI")
    except Exception as e:
        logging.error(f"Error calling OpenAI: {e}")
        reply = "Error calling OpenAI API."
    return jsonify({"reply": reply})

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    """
    Placeholder endpoint that confirms a button click.
    """
    logging.debug("Received a request at '/fetch_schema' endpoint")
    return jsonify({"message": "Fetch Schema button clicked (no action taken)."})

@app.route("/kpi_query", methods=["POST"])
def kpi_query():
    """
    Placeholder endpoint for KPI queries.
    """
    logging.debug("Received a request at '/kpi_query' endpoint")
    return jsonify({"status": "KPI query button clicked (no SQL executed)."})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
