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
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('title')
    result = {
        "title": title_tag.text if title_tag else None,
    }

    return result

def MD(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    meta_description = soup.find('meta', attrs={"name": "description"})
    result = {
        "description": meta_description['content'] if meta_description else None,
    }

    return result

def IL(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('main')  # Assuming "main" tag is used for main content
    if not main_content:
        main_content = soup.body  # Default to body if "main" tag is not found
    link_elements = main_content.find_all(['a', 'img'], recursive=True)
    
    broken_links = []
    for element in link_elements:
        link_url = element.get('href' if element.name == 'a' else 'src')
        if not link_url:
            continue
        try:
            r = requests.get(link_url, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                broken_links.append(link_url)
        except requests.RequestException:
            pass

    return {
        "broken_links": broken_links,
    }

def AnchorText(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('main')  # Assuming "main" tag is used for main content
    if not main_content:
        main_content = soup.body  # Default to body if "main" tag is not found
    anchor_elements = main_content.find_all('a', href=True)
    anchor_texts = [anchor.text.strip() for anchor in anchor_elements if anchor.text.strip()]

    return {
        "anchor_texts": anchor_texts,
    }

# Streamlit UI
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        # Title Tag Analysis
        title_tag_result = TT(url)
        st.subheader("Title Tag Audit")
        st.markdown(f"**Title Tag Content:** {title_tag_result['title']}")
        insights_title = get_gpt_insights(f"Provide a concise insight and recommendation for the title tag '{title_tag_result['title']}'.")
        st.markdown(f"**Insights:** {insights_title}")

        # Meta Description Analysis
        meta_description_result = MD(url)
        st.subheader("Meta Description Audit")
        if meta_description_result['description']:
            st.markdown(f"**Meta Description Content:** {meta_description_result['description']}")
        else:
            st.markdown("**Result:** Meta description is missing.")

        # Linking Audit
        linking_result = IL(url)
        st.subheader("Linking Audit")
        if linking_result['broken_links']:
            st.markdown("**Broken Links Identified:**")
            for link in linking_result['broken_links']:
                st.markdown(f"- {link}")

        # Anchor Text Audit
        anchor_text_result = AnchorText(url)
        st.subheader("Anchor Text Audit")
        for anchor in anchor_text_result['anchor_texts'][:5]:  # Displaying only first 5 for brevity
            insights_anchor = get_gpt_insights(f"Provide a concise insight for the anchor text '{anchor}'.")
            st.markdown(f"**Anchor Text:** {anchor}")
            st.markdown(f"**Insight:** {insights_anchor}")
