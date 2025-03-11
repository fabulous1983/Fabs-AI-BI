import logging
from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS handling
import openai
import os

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# OpenAI API Key (store securely)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    """
    Simple endpoint to handle chat between user and ChatGPT.
    """
    logging.debug("Received a request at '/chat' endpoint")

    # Get the data sent in the request
    data = request.json
    user_message = data.get("message", "")  # Get the user's message
    chat_history = data.get("chatHistory", "")  # Get the current chat history

    logging.debug(f"User Message: {user_message}")
    logging.debug(f"Chat History: {chat_history}")

    # Build the full message to send to ChatGPT (adding chat history to the current message)
    full_message = chat_history + f"\nUser: {user_message}"

    # Log the message being sent to OpenAI
    logging.debug(f"Sending to OpenAI: {full_message[:500]}...")  # Limit to first 500 chars for readability

    # Start the OpenAI request and log the action
    logging.debug("Sending request to OpenAI...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_message}]
        )
        logging.debug("Received response from OpenAI.")
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        return jsonify({"reply": "Sorry, there was an issue with the request."}), 500

    # Log the OpenAI response
    logging.debug(f"OpenAI Response: {response}")

    # Return the response from ChatGPT
    logging.debug("Returning response to the client.")
    return jsonify({"reply": response["choices"][0]["message"]["content"]})

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    """
    A placeholder for the 'fetch_schema' endpoint which is currently ignored.
    """
    logging.debug("Received a request at '/fetch_schema' endpoint")
    return jsonify({"message": "This endpoint is currently ignored and won't fetch anything."})

if __name__ == "__main__":
    # Log when the server starts
    logging.debug("Starting the Flask application...")

    # Run the Flask app (Only for local testing, Gunicorn should be used in production)
    port = int(os.getenv("PORT", 8080))  # Use the port specified by the environment, default 8080
    logging.debug(f"Running on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)  # Running on 0.0.0.0 to allow external access
