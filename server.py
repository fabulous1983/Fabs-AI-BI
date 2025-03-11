import logging
from flask import Flask, request, jsonify
import pyodbc
import openai
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app = Flask(__name__)

# OpenAI API Key (store securely)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database connection settings
DB_CONNECTION = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=sqlservercentralpublic.database.windows.net;DATABASE=AdventureWorks;UID=sqlfamily;PWD=sqlf@mily"

# Max data size (in MB) for queries
MAX_DATA_SIZE_MB = 100

@app.route("/fetch_schema", methods=["GET"])
def fetch_schema():
    """Fetch and summarize database schema"""
    logging.debug("fetch_schema called")
    
    conn = pyodbc.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS")
    schema = cursor.fetchall()
    conn.close()

    schema_text = "\n".join([f"{row[0]}: {row[1]}" for row in schema])
    
    # Log the schema to see what data is fetched
    logging.debug(f"Fetched schema: {schema_text[:500]}...")  # Only show first 500 characters for readability
    
    # Ask GPT to summarize the schema
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Summarize this database structure: {schema_text}"}]
    )
    
    logging.debug(f"GPT-3 Schema Response: {response}")
    return jsonify({"message": response["choices"][0]["message"]["content"]})

@app.route("/chat", methods=["POST"])
def chat():
    """Handle general user questions"""
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("chatHistory", "")
    
    # Log the incoming request
    logging.debug(f"User Message: {user_message}")
    logging.debug(f"Chat History: {chat_history}")

    full_message = chat_history + f"\nUser: {user_message}"

    # Log the message that is sent to OpenAI
    logging.debug(f"Sending to OpenAI: {full_message[:500]}...")  # Only show first 500 characters for readability

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": full_message}]
    )

    # Log the OpenAI response
    logging.debug(f"OpenAI Response: {response}")
    
    return jsonify({"reply": response["choices"][0]["message"]["content"]})

@app.route("/execute_sql", methods=["POST"])
def execute_sql():
    """Generate SQL based on user input and return query result"""
    data = request.json.get("chatHistory", "")

    # Ask ChatGPT to generate a SQL query
    logging.debug(f"Chat History for SQL: {data}")
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Generate a SQL query for: {data}"}]
    )
    
    sql_query = response["choices"][0]["message"]["content"]
    logging.debug(f"Generated SQL Query: {sql_query}")

    # Limiting the data fetched from the database
    try:
        conn = pyodbc.connect(DB_CONNECTION)
        logging.debug("Connected to database")
        df = pd.read_sql(sql_query, conn)
        
        # Check if data size exceeds the limit (100MB)
        data_size = df.memory_usage(deep=True).sum() / (1024 * 1024)  # Convert bytes to MB
        if data_size > MAX_DATA_SIZE_MB:
            logging.warning(f"Query result size is {data_size:.2f}MB, exceeding the {MAX_DATA_SIZE_MB}MB limit.")
            df = df.head(100)  # Limit data to first 100 rows (as an example)
        
        conn.close()
    except Exception as e:
        logging.error(f"Error executing SQL: {e}")
        return jsonify({"error": str(e)})

    # Log the dataset size after query execution
    logging.debug(f"Dataset fetched: {df.head(5)}")  # Log the first 5 rows to verify

    # Return the dataset
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

    logging.debug("Graph generated and encoded to base64.")
    return jsonify({"image": encoded_image})

if __name__ == "__main__":
    # Set the port based on environment variable (defaults to 8080)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
