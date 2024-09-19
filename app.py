__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import sqlite3


import streamlit as st 
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
from langchain_community.document_loaders import WebBaseLoader


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
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
    create_streamlit_app(chain, portfolio, clean_text)
    