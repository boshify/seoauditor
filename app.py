import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

# Progress bar messages
PROGRESS_MESSAGES = [
    "Casting SEO spells...",
    "Unleashing digital spiders...",
    "Diving into meta tags...",
    "Whispering to web spirits...",
    "Riding backlink waves...",
    "Decoding HTML matrix...",
    "Unraveling web yarn...",
    "Consulting the algorithm...",
    "Fetching search wisdom...",
    "Brewing the SEO potion..."
]

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
        "message": "",
        "audit_name": "Title Tag Audit"
    }

    if not title_tag:
        result["message"] = "Fail: Title tag is missing."
    elif len(title_tag.text) > 60:
        result["message"] = f"Fail: Title tag is too long ({len(title_tag.text)} characters)."
    elif len(title_tag.text) < 10:
        result["message"] = f"Fail: Title tag is too short ({len(title_tag.text)} characters)."
    else:
        result["message"] = "Pass: Title tag is within the recommended length."

    return result

def MD(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    meta_description = soup.find('meta', attrs={"name": "description"})
    
    result = {
        "description": meta_description['content'] if meta_description else None,
        "message": "",
        "audit_name": "Meta Description Audit"
    }

    if not meta_description or not meta_description.get('content'):
        result["message"] = "Fail: Meta description is missing."
    elif len(meta_description['content']) > 160:
        result["message"] = f"Fail: Meta description is too long ({len(meta_description['content'])} characters)."
    elif len(meta_description['content']) < 50:
        result["message"] = f"Fail: Meta description is too short ({len(meta_description['content'])} characters)."
    else:
        result["message"] = "Pass: Meta description is within the recommended length."

    return result

def IL(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    link_elements = soup.find_all(['a', 'img'], recursive=True)
    
    error_messages = []
    broken_links = []
    very_long_links = []
    access_errors = []
    resource_as_page_links = []
    
    progress_bar = st.progress(0)
    progress_text = st.empty()
    total_links = len(link_elements)

    for index, element in enumerate(link_elements):
        link_url = element.get('href' if element.name == 'a' else 'src')
        
        if not link_url:
            continue

        if len(link_url) > 200:
            very_long_links.append(link_url)

        try:
            r = requests.get(link_url, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                broken_links.append(link_url)
        except requests.RequestException as e:
            access_errors.append(link_url)

        if element.name == 'img' and element.parent.name == 'a':
            resource_as_page_links.append(link_url)

        progress_bar.progress((index + 1) / total_links)
        progress_text.text(PROGRESS_MESSAGES[index % len(PROGRESS_MESSAGES)])

    progress_bar.empty()
    progress_text.empty()

    too_many_links_message = ""
    if len(link_elements) > 100:
        too_many_links_message = f"This page has {len(link_elements)} on-page links which might be excessive."

    audit_data = {
        "broken_links": broken_links,
        "very_long_links": very_long_links,
        "access_errors": access_errors,
        "resource_as_page_links": resource_as_page_links,
        "too_many_links_message": too_many_links_message
    }

    prompt = f"Analyze the following internal linking audit data and provide a brief summarized analysis and recommendations in markdown format: \n\n{audit_data}"
    gpt_insights = get_gpt_insights(prompt)

    result = {
        "message": gpt_insights,
        "audit_name": "Linking Audit"
    }

    return result

def AnchorText(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    anchor_elements = soup.find_all('a', href=True)
    anchor_texts = [anchor.text.strip() for anchor in anchor_elements if anchor.text.strip()]
    combined_texts = "\n".join(anchor_texts)
    
    prompt = f"Analyze the following anchor texts and provide insights, analysis, and recommendations in markdown format using specific examples: \n\n{combined_texts}"
    insights = get_gpt_insights(prompt)

    return {
        "message": insights,
        "audit_name": "Anchor Text Audit"
    }

st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    title_results = TT(url)
    meta_results = MD(url)
    link_results = IL(url)
    anchor_text_results = AnchorText(url)

    results = [title_results, meta_results, link_results, anchor_text_results]

    for result in results:
        st.write("---")
        st.subheader(result["audit_name"])
        if 'title' in result and result["title"]:
            st.info(f"**Title Tag Content:** {result['title']}")
            insights = get_gpt_insights(f"Rate the title tag '{result['title']}' on a scale of 1 to 5 and provide an optimized version.")
            st.info(f"**GPT Insights:** {insights}")
        elif 'description' in result and result["description"]:
            st.info(f"**Meta Description Content:** {result['description']}")
            insights = get_gpt_insights(f"Rate the meta description '{result['description']}' on a scale of 1 to 5 and provide an optimized version.")
            st.info(f"**GPT Insights:** {insights}")

        st.info(f"**Result:** {result['message']}")
