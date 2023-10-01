import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

def get_gpt_insights(prompt):
    messages = [
        {"role": "system", "content": "You are an SEO expert."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    return response.choices[0].message['content'].strip()

def TT(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string
    insights = get_gpt_insights(f"Analyze the title tag: {title}")
    return title, insights

def MD(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        return meta_description['content']
    else:
        return None

def IL(url):
    # This is a placeholder for your Linking Audit logic
    # You'd replace the logic here with the actual implementation
    return "Linking Audit results go here"

def AnchorText(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anchor_texts = [a.string for a in soup.find_all('a') if a.string]
    insights = get_gpt_insights(f"Analyze the anchor texts: {', '.join(anchor_texts[:5])} and more")
    return anchor_texts, insights

st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        # Title Tag Audit
        with st.container():
            st.subheader("🏷️ Title Tag Audit")
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            st.write(f"**GPT Insights:** {title_insights}")

        # Meta Description Audit
        with st.container():
            st.subheader("📝 Meta Description Audit")
            meta_desc = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
            else:
                st.write("❌ Meta description is missing.")

        # Linking Audit
        with st.container():
            st.subheader("🔗 Linking Audit")
            linking_results = IL(url)
            st.write(linking_results)

        # Anchor Text Audit
        with st.container():
            st.subheader("⚓ Anchor Text Audit")
            anchor_texts, anchor_insights = AnchorText(url)
            st.write(f"**Sample Anchor Texts:** {', '.join(anchor_texts[:5])} and more...")
            st.write(f"**GPT Insights:** {anchor_insights}")
