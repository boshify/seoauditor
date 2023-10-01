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
        "what_it_is": "The title tag provides a brief summary of the content of the page and is displayed in search engine results and browser tabs.",
        "how_to_fix": "",
        "audit_name": "Title Tag Audit"
    }
    if not title_tag:
        result["message"] = "Fail: Title tag is missing."
        result["how_to_fix"] = "Add a title tag to the head section of your HTML."
    elif len(title_tag.text) > 60:
        result["message"] = f"Fail: Title tag is too long ({len(title_tag.text)} characters)."
        result["how_to_fix"] = "Reduce the length of the title tag to 60 characters or fewer."
    elif len(title_tag.text) < 10:
        result["message"] = f"Fail: Title tag is too short ({len(title_tag.text)} characters)."
        result["how_to_fix"] = "Increase the length of the title tag to at least 10 characters."
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
        "what_it_is": "The meta description provides a brief summary of the content of the page and is displayed in search engine results.",
        "how_to_fix": "",
        "audit_name": "Meta Description Audit"
    }
    if not meta_description or not meta_description.get('content'):
        result["message"] = "Fail: Meta description is missing."
        result["how_to_fix"] = "Add a meta description tag to the head section of your HTML with a relevant description of the page content."
    elif len(meta_description['content']) > 160:
        result["message"] = f"Fail: Meta description is too long ({len(meta_description['content'])} characters)."
        result["how_to_fix"] = "Reduce the length of the meta description to 160 characters or fewer."
    elif len(meta_description['content']) < 50:
        result["message"] = f"Fail: Meta description is too short ({len(meta_description['content'])} characters)."
        result["how_to_fix"] = "Increase the length of the meta description to at least 50 characters."
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
            very_long_links.append(f"Very long URL: {link_url}")
        try:
            r = requests.get(link_url, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                broken_links.append(f"Potential broken link (status {r.status_code}): {link_url}")
        except requests.RequestException as e:
            access_errors.append(f"Error accessing link ({e}): {link_url}")
        if element.name == 'img' and element.parent.name == 'a':
            resource_as_page_links.append(f"Resource img with URL {link_url} is formatted as a page link.")
        progress_bar.progress((index + 1) / total_links)
        progress_text.text(PROGRESS_MESSAGES[index % len(PROGRESS_MESSAGES)])
    progress_bar.empty()
    progress_text.empty()
    too_many_links_message = "This page might have too many on-page links." if len(link_elements) > 100 else ""
    gpt_insights = internal_link_analysis_gpt(error_messages, broken_links, very_long_links, access_errors, resource_as_page_links, too_many_links_message)
    return {
        "message": gpt_insights,
        "audit_name": "Linking Audit"
    }

def AnchorText(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    anchor_elements = soup.find_all('a', href=True)
    anchor_texts = [anchor.text.strip() for anchor in anchor_elements if anchor.text.strip()]
    combined_texts = "\n".join(anchor_texts)
    prompt = f"Analyze the following anchor texts and provide insights, analysis, and recommendations in markdown format: \n\n{combined_texts}"
    messages = [
        {"role": "system", "content": "You are an SEO expert analyzing anchor texts."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    return {
        "message": response.choices[0].message['content'].strip(),
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
            insights = get_gpt_insights(f"Analyze and provide insights for this title tag: '{result['title']}'")
            st.info(f"**GPT Insights:** {insights}")
        elif 'description' in result and result["description"]:
            st.info(f"**Meta Description Content:** {result['description']}")
            insights = get_gpt_insights(f"Analyze and provide insights for this meta description: '{result['description']}'")
            st.info(f"**GPT Insights:** {insights}")
        else:
            st.info(f"**Result:** {result['message']}")
