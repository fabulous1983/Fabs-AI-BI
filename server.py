import logging
from flask import Flask, request, jsonify
import openai
import os

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)

# OpenAI API Key (store securely)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    """
    Simple endpoint to handle chat between user and ChatGPT.
    """
    data = request.json
    user_message = data.get("message", "")  # Get the user's message
    chat_history = data.get("chatHistory", "")  # Get the current chat history

    logging.debug(f"User Message: {user_message}")
    logging.debug(f"Chat History: {chat_history}")

    # Build the message to send to ChatGPT
    full_message = chat_history + f"\nUser: {user_message}"

    # Log the message being sent to OpenAI
    logging.debug(f"Sending to OpenAI: {full_message[:500]}...")  # Limit to first 500 chars for readability

    # Make the API call to OpenAI for the response
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": full_message}]
    )

    # Log the OpenAI response
    logging.debug(f"OpenAI Response: {response}")

    # Return the response from ChatGPT
    return jsonify({"reply": response["choices"][0]["message"]["content"]})

if __name__ == "__main__":
    # Run the Flask app
    port = int(os.getenv("PORT", 8080))  # Use the port specified by the environment, default 8080
    app.run(host="0.0.0.0", port=port, debug=True)  # Running on 0.0.0.0 to allow external access
