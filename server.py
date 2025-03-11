from flask import Flask, request, jsonify
import pyodbc
import openai
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io
import os

app = Flask(__name__)

# OpenAI API Key (store securely)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database connection settings
DB_CONNECTION = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=sqlservercentralpublic.database.windows.net;DATABASE=AdventureWorks;UID=sqlfamily;PWD=sqlf@mily"

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    """Fetch and summarize database schema"""
    conn = pyodbc.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS")
    schema = cursor.fetchall()
    conn.close()

    schema_text = "\n".join([f"{row[0]}: {row[1]}" for row in schema])

    # Ask GPT to summarize the schema
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Summarize this database structure: {schema_text}"}]
    )
    
    return jsonify({"message": response["choices"][0]["message"]["content"]})

@app.route("/chat", methods=["POST"])
def chat():
    """Handle general user questions"""
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")

    # Combine user message with previous chat history
    full_message = chat_history + f"\nUser: {user_message}"

    # Send the full message to OpenAI for a response
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": full_message}]
    )

    return jsonify({"reply": response["choices"][0]["message"]["content"]})

@app.route("/execute_sql", methods=["POST"])
def execute_sql():
    """Generate SQL based on user input and return query result"""
    data = request.json.get("chatHistory", "")

    # Ask ChatGPT to generate a SQL query
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Generate a SQL query for: {data}"}]
    )
    
    sql_query = response["choices"][0]["message"]["content"]

    # Execute the generated SQL query on the database
    conn = pyodbc.connect(DB_CONNECTION)
    df = pd.read_sql(sql_query, conn)
    conn.close()

    # Convert the result into a dictionary
    return jsonify({"dataset": df.to_dict()})

@app.route("/generate_graph", methods=["POST"])
def generate_graph():
    """Generate a graph from the SQL result"""
    data = request.json.get("dataset")
    df = pd.DataFrame(data)

    # Generate a bar chart from the DataFrame
    plt.figure(figsize=(8, 4))
    df.plot(kind="bar")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    
    # Encode the graph as base64 to send as a response
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({"image": encoded_image})

if __name__ == "__main__":
    # Set the port based on environment variable (defaults to 8080)
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
