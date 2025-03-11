import logging
from flask import Flask, request, jsonify
from flask_cors import CORS  # Ensure this is installed
import os
from openai import ChatCompletion  # Import directly from openai

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the OpenAI API Key from environment variables (set via Fly secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
import openai
openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    logging.debug("Received request at /chat endpoint")
    
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")
    
    logging.debug(f"User Message: {user_message}")
    logging.debug(f"Chat History: {chat_history}")
    
    # Build the message including a system message for context
    full_message = chat_history + f"\nUser: {user_message}"
    logging.debug(f"Full message: {full_message[:500]}...")  # Show first 500 characters
    
    try:
        response = ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_message}
            ]
        )
        logging.debug("Received response from ChatCompletion.")
    except Exception as e:
        logging.error(f"Error during ChatCompletion request: {e}")
        return jsonify({"reply": "Error contacting ChatGPT API.", "debug": str(e)}), 500
    
    reply = response["choices"][0]["message"]["content"]
    logging.debug("Returning response to client.")
    return jsonify({"reply": reply, "debug": "ChatCompletion call succeeded."})

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    logging.debug("Received request at /fetch_schema endpoint")
    return jsonify({"message": "This endpoint is currently ignored.", "debug": "No schema fetched."})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
