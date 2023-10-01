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
    insights = None
    if meta_description:
        insights = get_gpt_insights(f"Analyze the meta description: {meta_description['content']}")
        return meta_description['content'], insights
    else:
        return None, "❌ Meta description is missing."

def IL(url):
    # Linking Audit logic
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')  # Extracting main content
    internal_links = [a['href'] for a in main_content.find_all('a') if a['href'].startswith(url)]
    
    insights = get_gpt_insights(f"Analyze the internal links in the main content of the webpage: {url}. The links are: {', '.join(internal_links)}")
    return insights

def AnchorText(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')  # Extracting main content
    if main_content:
        anchor_texts = [a.string for a in main_content.find_all('a') if a.string]
    else:
        anchor_texts = [a.string for a in soup.find_all('a') if a.string]
    
    recommendations = get_gpt_insights(f"Provide recommendations for optimizing the anchor texts: {', '.join(anchor_texts[:5])} and more")
    return anchor_texts, recommendations

st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        # Title Tag Audit
        with st.expander("🏷️ Title Tag Audit"):
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            st.write(f"**GPT Insights:** {title_insights}")

        # Meta Description Audit
        with st.expander("📝 Meta Description Audit"):
            meta_desc, meta_desc_insights = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
                st.write(f"**GPT Insights:** {meta_desc_insights}")
            else:
                st.write(meta_desc_insights)

        # Linking Audit
        with st.expander("🔗 Linking Audit"):
            linking_results = IL(url)
            st.write(linking_results)

        # Anchor Text Audit
        with st.expander("⚓ Anchor Text Audit"):
            anchor_texts, anchor_insights = AnchorText(url)
            st.write(f"**Sample Anchor Texts:** {', '.join(anchor_texts[:5])} and more...")
            st.write(f"**GPT Insights:** {anchor_insights}")
