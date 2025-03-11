import logging
import os
import openai
import pyodbc
import base64
import io
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OPENAI_API_KEY not set!")

# Public AdventureWorks DB credentials
DB_SERVER = "sqlservercentralpublic.database.windows.net"
DB_NAME   = "AdventureWorks"
DB_USER   = "sqlfamily"
DB_PWD    = "sqlf@m1ly"

lastQuery = None  # store the last generated query

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").upper().strip()
    logging.debug(f"User prompt: {prompt}")

    if "CREATE" in prompt:
        return handle_create(prompt)
    elif "FETCH" in prompt:
        return handle_fetch(prompt)
    elif "KPI" in prompt:
        return handle_kpi(prompt)
    elif "GRAPH" in prompt:
        return handle_graph(prompt)
    else:
        return jsonify({"error": "No recognized command found in prompt. Use CREATE, FETCH, KPI, or GRAPH."})

def handle_create(user_prompt):
    logging.debug("Handling CREATE command")

    conversation = [
        {"role": "system", "content": "You are a helpful SQL assistant. The user wants a SQL query to show the DB structure of AdventureWorks."},
        {"role": "user", "content": "Write a SQL query to show the full DB structure of the AdventureWorks database."}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=300,
            temperature=0
        )
        query_text = response.choices[0].message.content.strip()
        global lastQuery
        lastQuery = query_text
        return jsonify({"reply": f"Generated SQL Query:\n{query_text}"})
    except Exception as e:
        logging.error(f"Error in handle_create: {e}")
        return jsonify({"error": str(e)}), 500

def handle_fetch(user_prompt):
    logging.debug("Handling FETCH command")
    if not lastQuery:
        return jsonify({"error": "No query to fetch. Please CREATE a query first."})

    # Execute lastQuery
    try:
        rows = execute_sql(lastQuery)
    except Exception as e:
        logging.error(f"Error executing lastQuery: {e}")
        return jsonify({"error": str(e)}), 500

    # Convert rows to a string for ChatGPT
    row_str = "\n".join(str(r) for r in rows[:10])  # limit to first 10
    conversation = [
        {"role": "system", "content": "You are a helpful data analyst. The user wants to find the last 5 years revenue growth."},
        {"role": "user", "content": f"Here are some sample rows:\n{row_str}\nPropose how to find last 5 years revenue growth and give me a SQL query to do so."}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=300,
            temperature=0
        )
        chat_text = response.choices[0].message.content.strip()
        return jsonify({"reply": f"Executed Query:\n{lastQuery}\n\nChatGPT says:\n{chat_text}"})
    except Exception as e:
        logging.error(f"Error in handle_fetch ChatGPT: {e}")
        return jsonify({"error": str(e)}), 500

def handle_kpi(user_prompt):
    logging.debug("Handling KPI command")
    conversation = [
        {"role": "system", "content": "You are a helpful BI assistant. The user wants a Python script to create a KPI dashboard."},
        {"role": "user", "content": "Make a simple Python script to create a dashboard for the last 5 years revenue growth."}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=300,
            temperature=0
        )
        chat_text = response.choices[0].message.content.strip()
        return jsonify({"reply": f"ChatGPT proposes dashboard script:\n{chat_text}"})
    except Exception as e:
        logging.error(f"Error in handle_kpi: {e}")
        return jsonify({"error": str(e)}), 500

def handle_graph(user_prompt):
    logging.debug("Handling GRAPH command")
    try:
        # Dummy data for demonstration
        import random
        import datetime
        
        years = [datetime.datetime.now().year - i for i in range(4, -1, -1)]
        revenue = [random.randint(50, 150) for _ in years]

        plt.figure(figsize=(6,4))
        plt.plot(years, revenue, marker='o')
        plt.title("Revenue Growth (Dummy Data)")
        plt.xlabel("Year")
        plt.ylabel("Revenue (M USD)")
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close()
        
        return jsonify({
            "reply": "Generated a dummy revenue growth chart!",
            "graph": img_base64
        })
    except Exception as e:
        logging.error(f"Error generating graph: {e}")
        return jsonify({"error": str(e)}), 500

def execute_sql(query):
    """
    Connect to the public Azure AdventureWorks DB and execute the query.
    """
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PWD}"
    )
    logging.debug(f"Connecting to DB: {DB_SERVER}")
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        logging.debug(f"Executing query (first 200 chars): {query[:200]}...")
        cursor.execute(query)
        rows = cursor.fetchall()
    logging.debug("Query executed successfully.")
    return rows

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
