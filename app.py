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
    main_content = soup.find('main')  # Assuming "main" tag is used for main content
    if not main_content:
        main_content = soup.body  # Default to body if "main" tag is not found
    link_elements = main_content.find_all(['a', 'img'], recursive=True)
    
    broken_links = []
    very_long_links = []
    access_errors = []
    resource_as_page_links = []
    
    for element in link_elements:
        link_url = element.get('href' if element.name == 'a' else 'src')
        
        if not link_url:
            continue
        if len(link_url) > 200:
            very_long_links.append(link_url)

        try:
            r = requests.get(link_url, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                broken_links.append(link_url)
        except requests.RequestException:
            access_errors.append(link_url)

        if element.name == 'img' and element.parent.name == 'a':
            resource_as_page_links.append(link_url)

    prompt_content = "\n".join([
        "*Broken Links:* " + ", ".join(broken_links) if broken_links else "",
        "*Very Long URLs:* " + ", ".join(very_long_links) if very_long_links else "",
        "*Access Errors:* " + ", ".join(access_errors) if access_errors else "",
        "*Resource Images as Links:* " + ", ".join(resource_as_page_links) if resource_as_page_links else ""
    ])

    prompt = f"Analyze the internal linking audit results and provide a brief summarized analysis and recommendations based on the following data: \n\n{prompt_content}"
    insights = get_gpt_insights(prompt)

    return {
        "message": insights,
        "audit_name": "Linking Audit"
    }

def AnchorText(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('main')  # Assuming "main" tag is used for main content
    if not main_content:
        main_content = soup.body  # Default to body if "main" tag is not found
    anchor_elements = main_content.find_all('a', href=True)
    anchor_texts = [anchor.text.strip() for anchor in anchor_elements if anchor.text.strip()]
    combined_texts = "\n".join(anchor_texts)
    prompt = f"Provide an analysis and recommendations based on the following anchor texts: \n\n{combined_texts}"
    insights = get_gpt_insights(prompt)

    return {
        "message": insights,
        "audit_name": "Anchor Text Audit"
    }

# Streamlit UI
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        title_tag_result = TT(url)
        st.subheader(title_tag_result["audit_name"])
        st.write("Title Tag Content:", title_tag_result["title"])
        insights = get_gpt_insights(f"Analyze the title tag '{title_tag_result['title']}' and provide insights and optimization suggestions.")
        st.markdown(f"**GPT Insights:** {insights}")
        st.write(title_tag_result["message"])

        meta_description_result = MD(url)
        st.subheader(meta_description_result["audit_name"])
        st.write(meta_description_result["message"])

        linking_result = IL(url)
        st.subheader(linking_result["audit_name"])
        st.write(linking_result["message"])

        anchor_text_result = AnchorText(url)
        st.subheader(anchor_text_result["audit_name"])
        st.write(anchor_text_result["message"])
