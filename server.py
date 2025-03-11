import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Retrieve OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OPENAI_API_KEY not set!")

@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint for a simple chatbot interaction using OpenAI's API.
    The function builds a full message with a system prompt and the user input,
    then sends it to OpenAI and returns the response.
    """
    debug_logs = []
    debug_logs.append("Received request at /chat endpoint.")
    
    data = request.get_json()
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")
    
    debug_logs.append(f"User Message: {user_message}")
    debug_logs.append(f"Chat History: {chat_history}")
    
    # Build the full message including a system instruction
    full_message = chat_history + "\nUser: " + user_message
    debug_logs.append(f"Constructed full message (first 200 chars): {full_message[:200]}...")
    
    try:
        # Use the new API interface to create a chat completion.
        # Note: This call is now compatible with openai>=1.0.0.
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_message}
            ]
        )
        debug_logs.append("Received response from OpenAI.")
    except Exception as e:
        error_message = f"Error during OpenAI request: {e}"
        debug_logs.append(error_message)
        logging.error(error_message)
        return jsonify({"reply": "Error contacting OpenAI API.", "debug": debug_logs}), 500

    reply = completion.choices[0].message.content
    debug_logs.append("Returning response to client.")
    
    return jsonify({"reply": reply, "debug": debug_logs})

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    """
    A placeholder endpoint to confirm button clicks.
    """
    debug_logs = ["Received request at /fetch_schema endpoint."]
    return jsonify({"message": "This endpoint is currently ignored.", "debug": debug_logs})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
