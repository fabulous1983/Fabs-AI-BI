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
    conn = pyodbc.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS")
    schema = cursor.fetchall()
    conn.close()

    schema_text = "\n".join([f"{row[0]}: {row[1]}" for row in schema])
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Summarize this database structure: {schema_text}"}]
    )
    return jsonify({"message": response["choices"][0]["message"]["content"]})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    chat_history = data["chatHistory"]

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": chat_history}]
    )
    return jsonify({"reply": response["choices"][0]["message"]["content"]})

@app.route("/execute_sql", methods=["POST"])
def execute_sql():
    data = request.json["chatHistory"]

    # Ask ChatGPT to generate SQL query
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": f"Generate a SQL query for: {data}"}]
    )
    sql_query = response["choices"][0]["message"]["content"]

    conn = pyodbc.connect(DB_CONNECTION)
    df = pd.read_sql(sql_query, conn)
    conn.close()

    return jsonify({"dataset": df.to_dict()})

@app.route("/generate_graph", methods=["POST"])
def generate_graph():
    df = pd.DataFrame(request.json["dataset"])

    plt.figure(figsize=(8, 4))
    df.plot(kind="bar")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return jsonify({"image": encoded})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
