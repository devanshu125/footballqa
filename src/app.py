import streamlit as st
import os
import requests
import duckdb
import re
import json

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "nvidia/llama-3.3-nemotron-super-49b-v1:free"

# read the system prompt file
with open("../prompt_data_folder/system_prompt.txt", encoding="utf-8") as f:
    system_prompt = f.read()

# read table cols data prompt
with open("../prompt_data_folder/table_cols_data.txt", encoding="utf-8") as f:
    table_cols_prompt = f.read()

def send_to_openrouter(req_prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [

            {"role": "system", "content": [
                {"type": "text", "text": system_prompt},
                {"type": "text", "text": table_cols_prompt}
            ]},

            {"role": "user", "content": [
                {"type": "text", "text": req_prompt},
                {"type": "text", "text": "Refer to column names properly before creating the query. Give the SQL query in one line only in JSON output where key is 'sql_query' and value will be the query and write ```json."},
            ]}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def execute_safe_sql_from_dict(data: dict, db_path: str = ":memory:"):
    """
    Executes a validated, read-only SQL query provided under 'sql_query' in the input dictionary.

    Args:
        data (dict): A dictionary with a key 'sql_query' containing the SQL statement.
        db_path (str): Path to the DuckDB database file (default is in-memory).

    Returns:
        list: Query result rows.
    """
    # Extract the JSON object from the triple backtick block
    raw_content = data['choices'][0]['message']['content']
    # Extract the JSON block between triple backticks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_content, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON block found.")

    json_block = match.group(1)

    # Clean up and parse JSON
    try:
        data = json.loads(json_block)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    sql_query = data.get("sql_query", "").strip()
    if not sql_query:
        raise ValueError("No 'sql_query' key found in the JSON.")
    else:
        st.text(sql_query)

    # Attempt execution
    try:
        con = duckdb.connect(database=db_path)
        result = con.execute(sql_query).fetch_df()
        return result
    except Exception as e:
        raise ValueError(f"SQL execution failed: {e}")
    # return sql_query
    

req_user_prompt = st.text_input(label="What's your question?")
submit_button = st.button("Submit")
if submit_button:
    req_response = send_to_openrouter(req_prompt=req_user_prompt)
    st.header("LLM Response:")
    st.json(req_response)
    st.header("Extracted query:")
    result_data = execute_safe_sql_from_dict(req_response, db_path="../db_folder/footballqa.duckdb")
    st.dataframe(result_data)