import logging
import os
import openai
import pyodbc
import base64
import io
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from flask_cors import CORS

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OPENAI_API_KEY not set!")

# Database credentials for the public AdventureWorks DB
DB_SERVER = "sqlservercentralpublic.database.windows.net"
DB_NAME = "AdventureWorks"
DB_USER = "sqlfamily"
DB_PWD  = "sqlf@m1ly"

# We'll store a lastQuery in memory for demonstration. 
# In production, you might store queries in a session or DB.
lastQuery = None

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").upper().strip()
    logging.debug(f"User prompt: {prompt}")

    # Step 1: Check which command user wants
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
    """
    1) Ask ChatGPT to write a query that extracts the full DB structure
    2) Return that query to the webpage (store it in lastQuery if needed)
    """
    logging.debug("Handling CREATE command")

    # We'll ask ChatGPT to generate a SQL query to get the full DB structure
    conversation = [
        {"role": "system", "content": "You are a helpful SQL assistant."},
        {"role": "user", "content": "Write a SQL query to show the full DB structure of the AdventureWorks database."}
    ]
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=build_prompt(conversation),
            max_tokens=150,
            temperature=0
        )
        query_text = response.choices[0].text.strip()
        global lastQuery
        lastQuery = query_text  # store for later usage
        return jsonify({"reply": f"Generated SQL Query:\n{query_text}"})
    except Exception as e:
        logging.error(f"Error in handle_create: {e}")
        return jsonify({"error": str(e)}), 500

def handle_fetch(user_prompt):
    """
    1) We have lastQuery from handle_create or something
    2) Execute that query (if any) and return the output to ChatGPT 
       asking it to propose how to find the last 5 years revenue growth
    """
    logging.debug("Handling FETCH command")
    if not lastQuery:
        return jsonify({"error": "No query to fetch. Please CREATE a query first."})

    # Execute lastQuery
    rows = []
    try:
        rows = execute_sql(lastQuery)
    except Exception as e:
        logging.error(f"Error executing lastQuery: {e}")
        return jsonify({"error": str(e)}), 500
    
    # Convert rows to a string for ChatGPT
    row_str = "\n".join(str(r) for r in rows[:10])  # limit to first 10 rows for brevity
    # Next, ask ChatGPT how to find last 5 years revenue growth 
    conversation = [
        {"role": "system", "content": "You are a helpful data analyst."},
        {"role": "user", "content": f"Here is some data:\n{row_str}\nPropose how to find last 5 years revenue growth and give me a SQL query to do so."}
    ]
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=build_prompt(conversation),
            max_tokens=250,
            temperature=0
        )
        chat_text = response.choices[0].text.strip()
        return jsonify({"reply": f"Executed Query:\n{lastQuery}\n\nChatGPT says:\n{chat_text}"})
    except Exception as e:
        logging.error(f"Error in handle_fetch ChatGPT: {e}")
        return jsonify({"error": str(e)}), 500

def handle_kpi(user_prompt):
    """
    1) Suppose user wants us to "go execute the query, return to ChatGPT
       and ask it to make a dashboard script"
    """
    logging.debug("Handling KPI command")
    # We can reuse lastQuery or let ChatGPT create a new KPI-based query
    # For demonstration, let's just ask ChatGPT for a "dashboard script"
    conversation = [
        {"role": "system", "content": "You are a helpful BI assistant."},
        {"role": "user", "content": "Make a simple Python script to create a dashboard for the last 5 years revenue growth."}
    ]
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=build_prompt(conversation),
            max_tokens=300,
            temperature=0
        )
        chat_text = response.choices[0].text.strip()
        return jsonify({"reply": f"ChatGPT proposes dashboard script:\n{chat_text}"})
    except Exception as e:
        logging.error(f"Error in handle_kpi: {e}")
        return jsonify({"error": str(e)}), 500

def handle_graph(user_prompt):
    """
    1) Actually generate a graph in Python with matplotlib
    2) Return the base64 image to the webpage
    """
    logging.debug("Handling GRAPH command")
    try:
        # For demonstration, let's plot a dummy revenue growth line
        import random
        import datetime
        
        # Create dummy data
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

def build_prompt(conversation):
    """
    For older openai==0.28.0 usage with text-davinci-003,
    we build a prompt from a conversation array (system/user).
    """
    # Minimal approach: system => instructions, user => question
    prompt_str = ""
    for c in conversation:
        if c["role"] == "system":
            prompt_str += f"System: {c['content']}\n"
        elif c["role"] == "user":
            prompt_str += f"User: {c['content']}\n"
    prompt_str += "Answer:\n"
    return prompt_str

def execute_sql(query):
    """
    Connects to the public AdventureWorks DB and executes the given query.
    Returns a list of rows.
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
        logging.debug(f"Executing query: {query[:200]}...")
        cursor.execute(query)
        rows = cursor.fetchall()
    logging.debug("Query executed successfully.")
    return rows

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logging.debug(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
