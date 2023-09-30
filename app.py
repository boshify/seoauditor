import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Set your OpenAI API key
openai.api_key = "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"

# Function to crawl a webpage and return its source code
def crawl_page(url):
    headers = {'User-Agent': 'YOUR_FAKE_USER_AGENT_HERE'}  # Replace with a fake user agent
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Failed to fetch the page. Status code: {response.status_code}")
        return None

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
source_code = crawl_page(url)

if source_code:
    st.text("Page Source Code:")
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
