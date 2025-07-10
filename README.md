# 💬 Chat with Database Response

This is a Streamlit web application that allows you to chat with your MySQL database using natural language. It uses OpenAI's GPT model and LangChain to generate SQL queries, visualize data as bar charts, and download responses as PDFs.

---

## 📦 Features

- Ask natural language questions about your MySQL database.
- Automatically generate and run SQL queries.
- Display responses in human-readable format.
- Extract chartable data and visualize it as bar charts.
- Export responses as downloadable PDFs.

---

## 🧰 Tech Stack

- Python
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [OpenAI GPT](https://platform.openai.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- MySQL
- Pandas
- FPDF
- dotenv

---

## 🚀 Getting Started

### 1. Clone the repository

- git clone https://github.com/amaandx09/ChatWithDatabase.git
- cd ChatWithDatabase

### 2. Create a virtual environment and activate it
- python -m venv venv
- source venv/bin/activate   # On Windows: venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add your OpenAI API key
- Create a .env file in the root directory:
- OPENAI_API_KEY=your_openai_api_key
- ⚠️ Do not share your API key publicly.

### 5. Configure your database
- Edit the database config in the script
- DATABASE_NAME = "openaidb"
- db_uri = "mysql+pymysql://root:root@localhost:3306/openaidb"

### ▶️ Run the Application
- streamlit run main.py
- Visit http://localhost:8501 in your browser.


### ✨ How to Use
    1. Type a natural language question like:
        Show top 5 customers by revenue.
        List all products added in June.
        What is the average order value?

    2. The assistant will:
        Translate your question into SQL
        Run the query
        Display readable results

    3. You can:
        Click 📊 Show Chart to visualize bar chart (if applicable)
        Click Download PDF to export the result

### 🖼 Example Queries
- List top 10 products by sales
- Show total revenue per month
- What is the average order value for 2023?
- List employees hired after 2020

### 📂 Project Structure
- ChatWithDatabase/
- ├── main.py               # Main Streamlit app
- ├── .env                  # Your OpenAI API key
- ├── requirements.txt      # Python dependencies
- ├── README.md             # Project documentation


### 🙏 Acknowledgements
- OpenAI
- LangChain
- Streamlit
- FPDF
- SQLAlchemy

### 💡 Contributing
Pull requests are welcome! If you’d like to suggest improvements or add new features, feel free to fork this repo and create a PR.

### 📄 License
This project is licensed under the MIT License.



