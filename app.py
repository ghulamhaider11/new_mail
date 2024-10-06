__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import sqlite3


import streamlit as st 
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
from langchain_community.document_loaders import WebBaseLoader

# Add enhanced background image and custom CSS
def add_background_and_css():
    st.markdown(
        """
        <style>
        /* Background styling */
        .stApp {
            background-image: url('https://www.example.com/beautiful-background.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Arial', sans-serif;
        }
        
        /* Centering the page title with beautiful font */
        .stTitle {
            text-align: center;
            font-family: 'Helvetica', sans-serif;
            color: #ffffff;
            font-size: 48px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            padding-bottom: 20px;
        }
        
        /* Styling sidebar */
        .css-1d391kg {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
        }

        /* Styling text input box */
        .stTextInput > div > input {
            background-color: #f1f1f1;
            border: 2px solid #cccccc;
            border-radius: 10px;
            padding: 10px;
            width: 100%;
            transition: all 0.3s ease-in-out;
        }
        
        .stTextInput > div > input:focus {
            border-color: #0099ff;
            box-shadow: 0px 0px 10px rgba(0, 153, 255, 0.5);
        }

        /* Styling buttons */
        .stButton > button {
            background-color: #0066cc;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 15px;
            padding: 12px 20px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #005bb5;
            box-shadow: 0px 8px 15px rgba(0, 102, 204, 0.2);
            transform: translateY(-2px);
        }
        
        /* Styling code blocks */
        pre {
            background-color: #333333;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Add custom scroll bar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-thumb {
            background-color: #888;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: #555;
        }

        /* Adding animation to error messages */
        .stError {
            color: #ff4d4d;
            font-size: 18px;
            font-weight: bold;
            animation: shake 0.5s ease-in-out;
        }
        
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }

        </style>
        """,
        unsafe_allow_html=True
    )

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    # Sidebar for input
    with st.sidebar:
        url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-38714?from=job%20search%20funnel")
        submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = loader.load()
            if not data:
                st.error("Failed to load content from the URL")
                return

            page_content = data.pop().page_content
            st.write("Page content loaded successfully")  # Debugging line
            clean_data = clean_text(page_content)
            st.write(clean_data[:500])  # Preview first 500 characters of cleaned data

            portfolio.load_portfolio()
            jobs = llm.extract_jobs(clean_data)

            if not jobs:
                st.error("No jobs found in the page content")
            else:
                for job in jobs:
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills)
                    st.write(f"Skills: {skills}")
                    st.write(f"Links: {links}")
                    email = llm.write_mail(job, links)
                    st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    add_background_and_css()  # Call the function to apply background and CSS
    create_streamlit_app(chain, portfolio, clean_text)
