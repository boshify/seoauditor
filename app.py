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

def get_gpt_insights(content, content_type):
    messages = [
        {"role": "system", "content": "You are an SEO expert."},
        {"role": "user", "content": f"Rate the {content_type} '{content}' on a scale of 1 to 5 and provide an optimized version. Your rating should include the text 'out of 5'. Do not say I would give it. Just output the rating. For your better version, only output the better version and no additional text except for 'Try This:'."}
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

    # Find anchor tags within certain parent elements that users might interact with
    link_parents = ['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'figcaption']
    visible_links = []

    for parent in link_parents:
        for tag in soup.find_all(parent):
            visible_links.extend(tag.find_all('a', href=True))

    # Deduplicate
    visible_links = list({link['href']: link for link in visible_links}.values())
    
    error_links = []
    long_links = []
    broken_links = []
    resource_as_link = []
    img_links = []

    for link_element in visible_links:
        link = link_element['href']

        if len(link) > 200:  # Arbitrary length for "too long" URL
            long_links.append(link)
            continue

        try:
            r = requests.get(link, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                broken_links.append(f"{link} (status {r.status_code})")
        except Exception as e:
            error_links.append(f"{link} ({str(e)})")

        # Checking for resources formatted as links
        if link_element.name == "img":
            img_links.append(link)
            if not any(ext in link for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                resource_as_link.append(link)

        # Construct the results message
    messages = []
    if error_links:
        messages.append("Error accessing links:\n" + '\n'.join(error_links))
    if long_links:
        messages.append("Very long URLs:\n" + '\n'.join(long_links))
    if broken_links:
        messages.append("Broken links:\n" + '\n'.join(broken_links))
    if len(visible_links) > 100:  # Arbitrary number for "too many" links
        messages.append("This page has too many on-page links.")
    if resource_as_link:
        messages.append("Resources formatted as page links:\n" + '\n'.join(resource_as_link))
    if img_links:
        messages.append("Images as links:\n" + '\n'.join(img_links))


    result = {
        "message": "\n\n".join(messages),
        "what_it_is": "Linking checks for the page.",
        "how_to_fix": "Each link issue is categorized. Review the specific issue category for recommendations.",
        "audit_name": "Linking Audit"
    }

    return result

# Streamlit app interface and logic

st.title('SEO Audit Tool')
st.write('Provide a URL to get insights on its SEO.')

url = st.text_input('Enter URL:', 'https://www.example.com')

if url:
    progress = st.progress(0)
    progress_bar_steps = len(PROGRESS_MESSAGES)
    for i, msg in enumerate(PROGRESS_MESSAGES):
        progress.text(msg)
        progress.progress((i+1)/progress_bar_steps)

    # Call the functions and get results
    title_results = TT(url)
    meta_results = MD(url)
    link_results = IL(url)

    # Display results
    for result in [title_results, meta_results, link_results]:
        st.subheader(result['audit_name'])
        st.write(result['message'])
        st.write("What it is:", result['what_it_is'])
        st.write("How to fix:", result['how_to_fix'])
