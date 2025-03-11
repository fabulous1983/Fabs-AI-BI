import logging
from flask import Flask, request, jsonify
import os
from flask_cors import CORS

# Import ChatCompletion from openai (new recommended usage)
from openai import ChatCompletion
import openai

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# OpenAI API Key (set as an environment variable via Fly.io secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    """
    Simple endpoint to handle chat between user and ChatGPT.
    """
    logging.debug("Received request at '/chat' endpoint")
    
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")
    
    logging.debug(f"User Message: {user_message}")
    logging.debug(f"Chat History: {chat_history}")
    
    # Construct the full message
    full_message = chat_history + "\nUser: " + user_message
    logging.debug(f"Full message to send: {full_message[:500]}...")  # Log first 500 characters
    
    try:
        # Use the new ChatCompletion endpoint
        response = ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_message}]
        )
        logging.debug("Received response from ChatCompletion.")
    except Exception as e:
        logging.error(f"Error during ChatCompletion: {e}")
        return jsonify({"reply": "Error contacting ChatGPT API."}), 500

    return jsonify({"reply": response["choices"][0]["message"]["content"]})

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    logging.debug("Received request at '/fetch_schema' endpoint")
    return jsonify({"message": "This endpoint is currently ignored and won't fetch anything."})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
