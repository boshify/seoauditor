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
    try:
        response = requests.get(url)
        response.raise_for_status()
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
    except requests.RequestException as e:
        st.warning(f"Error fetching the URL. Details: {e}")
        return None

def MD(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
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
    except requests.RequestException as e:
        st.warning(f"Error fetching the URL. Details: {e}")
        return None

def IL(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all links, scripts, images, and CSS references
        link_elements = soup.find_all(['a', 'script', 'link', 'img'])
        
        error_messages = []
        
        progress_bar = st.progress(0)
        progress_text = st.empty()
        total_links = len(link_elements)
        
        for index, element in enumerate(link_elements):
            link_url = None
            
            if element.name == 'a':
                link_url = element.get('href')
            elif element.name == 'script' or element.name == 'img':
                link_url = element.get('src')
            elif element.name == 'link':
                link_url = element.get('href')

            # Check if URL is valid and not empty
            if not link_url:
                continue

            # Check if the link is external
            if not link_url.startswith(('http', '//')):
                continue

            # Check for HTTPS to HTTP links
            if url.startswith('https') and link_url.startswith('http://'):
                error_messages.append(f"Link from HTTPS to non-secure page: {link_url}")

            # Check for long URLs
            if len(link_url) > 200:
                error_messages.append(f"Very long URL: {link_url}")

            try:
                r = requests.get(link_url, allow_redirects=True, timeout=5)
                
                # Check for 403 status for external resources
                if r.status_code == 403:
                    error_messages.append(f"External resource forbidden (403): {link_url}")

                # Check for broken links
                elif r.status_code >= 400:
                    error_messages.append(f"Broken link (status {r.status_code}): {link_url}")

            except requests.RequestException as e:
                error_messages.append(f"Error accessing link ({e}): {link_url}")

            # Update the progress bar with rotating messages
            progress_bar.progress((index + 1) / total_links)
            progress_text.text(PROGRESS_MESSAGES[index % len(PROGRESS_MESSAGES)])

        # Check for too many on-page links
        if len(link_elements) > 100:
            error_messages.append("This page has too many on-page links.")

        # Check for resources formatted as page links
        for element in soup.find_all(['script', 'link', 'img']):
            if element.parent.name == 'a':
                error_messages.append(f"Resource {element.name} with URL {element.get('src' or 'href')} is formatted as a page link.")

        # Check for incorrect hreflang links
        for element in soup.find_all('link', attrs={"hreflang": True}):
            hreflang_url = element.get('href')
            try:
                r = requests.get(hreflang_url, allow_redirects=True, timeout=5)
                if r.status_code >= 400:
                    error_messages.append(f"Incorrect hreflang link with URL {hreflang_url}")
            except requests.RequestException as e:
                error_messages.append(f"Error accessing hreflang link ({e}): {hreflang_url}")

        # Clear progress once done
        progress_bar.empty()
        progress_text.empty()

        result = {
            "message": "",
            "what_it_is": "Linking checks for the page.",
            "how_to_fix": "",
            "audit_name": "Linking Audit"
        }

        if error_messages:
            result["message"] = "\n\n".join(error_messages)
        else:
            result["message"] = "Pass: No linking issues found."

        return result
    except requests.RequestException as e:
        return {
            "message": f"Error fetching the URL. Details: {e}",
            "what_it_is": "Linking checks for the page.",
            "how_to_fix": "Ensure the URL is correct and accessible.",
            "audit_name": "Linking Audit"
        }

def run_audits(url):
    return [TT(url), MD(url), IL(url)]

# Streamlit App
st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    results = run_audits(url)
    for result in results:
        st.write("---")  # Line break
        st.subheader(result["audit_name"])  # Displaying the custom audit name

        if 'title' in result and result["title"]:
            st.info(f"**Title Tag Content:** {result['title']}")
            insights = get_gpt_insights(result["title"], "title tag")
            st.info(f"**GPT Insights:** {insights}")
        elif 'description' in result and result["description"]:
            st.info(f"**Meta Description Content:** {result['description']}")
            insights = get_gpt_insights(result["description"], "meta description")
            st.info(f"**GPT Insights:** {insights}")

        st.info(f"**Result:** {result['message']}\n\n*What it is:* {result['what_it_is']}\n\n*How to fix:* {result['how_to_fix']}")
