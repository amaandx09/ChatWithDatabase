import os
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from dotenv import load_dotenv
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import create_engine,text
load_dotenv()


# Set up the engine and db
DATABASE_NAME = "openaidb" # Your Database name
db_uri = "mysql+pymysql://root:root@localhost:3306/openaidb" # Your db_uri
engine = create_engine(db_uri)

# Initialize LangChain's SQLDatabase with just the engine
db = SQLDatabase(engine=engine)

# Chart Output Model
class ChartBarField(BaseModel):
    x_labels: list[str]
    y_values: list[float]

# Chat Model Initialization
def init_chat_model():
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
        temperature=0,
        model="gpt-3.5-turbo"
    )
    
# run sql query with columsn and rows details
def run_sql_with_columns(sql_query):
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        columns = result.keys()
        rows = result.fetchall()
        return columns, rows

# This method convert sql to readable form
def convert_sql_result_to_readable(results: list) -> str:
    if not results:
        return "No data found."

    entries = []
    for index, result in enumerate(results, start=1):
        if len(results)!=1:
            lines = [f"{index}."]
        else:
            lines = []
        for key, value in result.items():
            label = key.replace('_', ' ').capitalize()
            lines.append(f"{label}: {value}")
        entries.append('\n'.join(lines))

    return '\n\n'.join(entries)
            
# Convert text to chart data
def get_response_list_key_and_values(text):
    output_parser = PydanticOutputParser(pydantic_object=ChartBarField)

    human_template = """
You are given a text. Extract all relevant label and numeric value pairs suitable for a bar chart.

Return the result as a JSON object with the following fields:
- "x_labels": a list of strings (the labels)
- "y_values": a list of numbers (the corresponding values)

If no such pairs are found, return:
{{ 
  "x_labels": [], 
  "y_values": [] 
}}

Text:
\"\"\"{request}\"\"\"

Format your answer like this:
{format_instruction}
"""
    chat_prompt = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(human_template),
    ])
    format_instruction = output_parser.get_format_instructions()

    formatted_chat_prompt = chat_prompt.format_messages(
        request=text,
        format_instruction=format_instruction
    )
    chat = init_chat_model()
    response = chat.invoke(formatted_chat_prompt)
    response_parser = output_parser.parse(response.content)
    return [response_parser.x_labels, response_parser.y_values]

# PDF Generator
def generate_pdf(text):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)

        buffer = BytesIO()
        pdf_bytes = bytes(pdf.output(dest='S').encode('latin-1'))
        buffer.write(pdf_bytes)
        buffer.seek(0)
        return buffer

    except Exception as e:
        return None  # Or raise a custom exception if needed

# SQL Model Prompt
def generate_sql_prompt(user_input, table_info):
    return f"""
You are a helpful SQL expert.
Given the following user request:
\"\"\"{user_input}\"\"\"

And these MySQL tables and columns:
{table_info}

Write a syntactically correct MySQL query that answers the request.
ONLY return the SQL code. No explanation.
"""

# Prepare table info string once
def get_table_info_string():
    table_names = db.get_usable_table_names()
    table_info = ""
    for table in table_names:
        try:
            table_info += f"\n{table}:\n{db.get_table_info([table])}\n"
        except Exception:
            continue  # skip broken tables
    return table_info[:4000]  # truncate if needed

# Table information
table_info_summary = get_table_info_string() +f"""
NOTE: The current database is named '{DATABASE_NAME}'. Use this in WHERE clauses when querying `information_schema.tables`.
"""

# Fast response function
def get_response(user_input):
    # Normalize input for greeting detection
    normalized_input = user_input.strip().lower()
    # Simple greeting or non-SQL intent detection
    if normalized_input in {"hi", "hello", "hey", "help", "who are you", "what can you do"}:
        return "Hi! Im your **Database Assistant.You can ask me things like: related database query."
   
    chat = init_chat_model()
    prompt = generate_sql_prompt(user_input, table_info_summary)
    sql_query = chat.invoke(prompt).content
    

    try:
        # Run SQL and get column names + data
        columns, rows = run_sql_with_columns(sql_query)
        
        # Convert to readable list of dicts
        result_data = [dict(zip(columns, row)) for row in rows]

        readable = convert_sql_result_to_readable(result_data)
        return f"**SQL Query:**\n```sql\n{sql_query}\n```\n\n**Answer:**\n\n{readable}"
    except Exception as e:
        return f"❌ SQL Error:\n\n```sql\n{sql_query}\n```\n\n**Error:** {e}"


    
    # try:
    #     result = db.run(sql_query)
    #     print("Result :",result)
    #     readable = convert_sql_result_to_readable(user_input,result)
    #     return f"**Answer is:**\n\n{readable}"
    #     return f"**SQL Query:**\n```sql\n{sql_query}\n```\n\n**Result:**\n{result}"
    # except Exception as e:
    #     return f"❌ SQL Error:\n\n```sql\n{sql_query}\n```\n\n**Error:** {e}"


## Streamlit Page Setup

st.set_page_config(page_title="Chat With Table Response", page_icon="💬")
st.title("💬 Chat With Table Response")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_bot_response" not in st.session_state:
    st.session_state.last_bot_response = ""

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

# Handle User Input
user_input = st.chat_input("Type your message here...")

# User query
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"), st.spinner("Thinking..."):
        try:
            bot_response = get_response(user_input)
        except Exception as e:
            bot_response = f"❌ Error: {e}"

        st.session_state.messages.append(
            {"role": "assistant", "content": bot_response})
        st.session_state.last_bot_response = bot_response
        st.text(bot_response)

# Extra Buttons
if st.session_state.last_bot_response:
    col1, col2 = st.columns(2)
    x_labels = None
    y_values = None

    with col1:
        if st.button("📊 Show Chart"):
            x_labels, y_values = get_response_list_key_and_values(
                st.session_state.last_bot_response)

    if x_labels and y_values:
        df = pd.DataFrame({'Label': x_labels, 'Value': y_values})
        st.bar_chart(df.set_index("Label"))
    elif x_labels == [] and y_values == []:
        st.warning("No chartable data found.")

    with col2:
        pdf_buffer = generate_pdf(st.session_state.last_bot_response)
        if pdf_buffer:
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="chat_response.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Error generating PDF. Please try again.")
        

