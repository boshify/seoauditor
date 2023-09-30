import streamlit as st
import requests
import openai

# Set your OpenAI API key securely using Streamlit secrets.toml
openai.api_key = st.secrets["openai_api_key"]

# Function to crawl a webpage and return its source code
def crawl_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Failed to fetch the page. Status code: {response.status_code}")
        return None

# Function to generate answers using GPT-3
def generate_answers(question, source_code, model="gpt-3.5-turbo-16k"):
    combined_prompt = f"Here's the source code of a webpage:\n{source_code}\n\nQuestion: {question}\nAnswer:"
    response = openai.Completion.create(
        engine=model,
        prompt=combined_prompt,
        max_tokens=150  # Adjust the max tokens based on your requirements
    )
    return response.choices[0].text.strip()

# Main Streamlit app
st.title("SEO Auditor")

url = st.text_input("Enter URL")

if st.button("Scan"):
    if not url:
        st.warning("Please enter a URL before scanning.")
    else:
        source_code = crawl_page(url)
        if source_code:
            st.text("Page Source Code:")
            st.code(source_code, language="html")

            question = st.text_input("Enter your question about the page")
            if question:
                answer = generate_answers(question, source_code)
                st.text("Answers:")
                st.write(answer)
