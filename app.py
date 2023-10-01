import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai
from tenacity import retry, wait_fixed, stop_after_attempt

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

@retry(wait=wait_fixed(3), stop=stop_after_attempt(3))
def get_link_status(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(link, headers=headers, allow_redirects=True, timeout=10)
    return response.status_code

def IL(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Only fetch anchor tags with visible text
    links = [link for link in soup.find_all('a', href=True) if link.text.strip()]
    
    base_url = url.rsplit('/', 1)[0]
    error_links = []
    progress_bar = st.progress(0)
    progress_text = st.empty()
    total_links = len(links)

    for index, link_element in enumerate(links):
        link = link_element['href']

        # Handle relative URLs
        if link.startswith('/'):
            link = base_url + link

        try:
            status = get_link_status(link)
            if status >= 400:
                error_links.append(link)
        except:
            error_links.append(link)

        # Update the progress bar with rotating messages
        progress_bar.progress((index + 1) / total_links)
        progress_text.text(PROGRESS_MESSAGES[index % len(PROGRESS_MESSAGES)])

    progress_text.empty()

    result = {
        "message": "",
        "what_it_is": "Internal linking refers to any links from one page of a domain that lead to another page within the same domain. It's crucial for both website navigation and SEO.",
        "how_to_fix": "",
        "audit_name": "Internal Linking Audit"
    }

    if error_links:
        result["message"] = "Fail: Found broken or incorrect links."
        result["how_to_fix"] = f"Fix or remove the following broken links: {', '.join(error_links)}"
    else:
        result["message"] = "Pass: No broken internal links found."

    return result

# Streamlit App
st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    results = [TT(url), MD(url), IL(url)]
    for result in results:
        st.write("<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>")  # Barrier
        st.subheader(result["audit_name"])  # Displaying the custom audit name

        if 'title' in result and result["title"]:
            st.info(f"**Title Tag Content:**\n```{result['title']}```")
            gpt_insights = get_gpt_insights(result["title"], "title tag")
            st.info(f"**GPT Insights:** {gpt_insights}")
        elif 'description' in result and result["description"]:
            st.info(f"**Meta Description Content:**\n```{result['description']}```")
            gpt_insights = get_gpt_insights(result["description"], "meta description")
            st.info(f"**GPT Insights:** {gpt_insights}")
        
        st.info(f"**Result:** {result['message']}\n\n*What it is:* {result['what_it_is']}\n\n*How to fix:* {result['how_to_fix']}")
