import logging
from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# OpenAI API Key (should be set in Fly.io secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    debug_logs = []
    debug_logs.append("Received request at /chat endpoint.")
    
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")
    debug_logs.append(f"User Message: {user_message}")
    debug_logs.append(f"Chat History: {chat_history}")
    
    full_message = chat_history + "\nUser: " + user_message
    debug_logs.append("Constructed full message for OpenAI.")
    debug_logs.append("Sending request to OpenAI...")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_message}]
        )
        debug_logs.append("Received response from OpenAI.")
    except Exception as e:
        debug_logs.append(f"Error during OpenAI request: {e}")
        return jsonify({"reply": "Error contacting OpenAI API.", "debug": debug_logs}), 500

    reply = response["choices"][0]["message"]["content"]
    debug_logs.append("Returning response to client.")
    return jsonify({"reply": reply, "debug": debug_logs})

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    debug_logs = []
    debug_logs.append("Received request at /fetch_schema endpoint.")
    return jsonify({"message": "This endpoint is currently ignored.", "debug": debug_logs})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
