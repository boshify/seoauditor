import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Set your OpenAI API key securely using Streamlit secrets.toml
openai.api_key = st.secrets["openai_api_key"]

# Function to crawl a webpage and return its source code
@st.cache  # Caching the function to avoid repeated requests
def crawl_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        st.error(f"Error fetching URL {url}: {e}")
        return ""

    return response.text

# Function to analyze SEO based on the source code
def analyze_seo(source_code):
    # Implement your SEO analysis logic here
    # You can use libraries like BeautifulSoup to parse and analyze the HTML
    pass

# Function to generate answers using GPT-3
def generate_answers(question, model="gpt-3.5-turbo-16k"):
    response = openai.Completion.create(
        engine=model,
        prompt=question,
        max_tokens=50  # Adjust the max tokens based on your requirements
    )
    return response.choices[0].text

# Main Streamlit app
st.title("SEO Auditor")

url = st.text_input("Enter URL")
stored_url = ""

if st.button("Scan"):
    if not url:
        st.warning("Please enter a URL before scanning.")
    else:
        stored_url = url  # Store the URL
        source_code = crawl_page(url)
        if source_code:
            st.text("Page Source Code:")
            with st.expander("Click to expand/collapse"):
                st.code(source_code, language="html")

            questions = st.text_area("Enter your questions")

            if st.button("Get Answers"):
                seo_recommendations = analyze_seo(source_code)
                if seo_recommendations:
                    st.text("SEO Recommendations:")
                    st.write(seo_recommendations)

                if questions:
                    answer = generate_answers(questions)
                    st.text("Answers:")
                    st.write(answer)

# Set the URL input field back to the stored URL
if stored_url:
    st.text_input("Enter URL", value=stored_url)
