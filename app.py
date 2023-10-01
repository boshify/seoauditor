import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

def get_rating_and_tip(content, content_type):
    """
    Uses GPT-3.5-turbo-16k to rate the content and provide a quick tip for improvement.
    """
    messages = [
        {"role": "system", "content": "You are an SEO expert."},
        {"role": "user", "content": f"Rate the {content_type} '{content}' on a scale of 1 to 5 and provide a better version. Your rating should include the text 'out of five'. Do not say i would give it. Just output the rating. For your better version, only output the better version and no additional text."}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()

# <><><><><><><> START OF FUNCTION TT <><><><><><><>

def TT(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {
            "title": None, 
            "message": "Error: Could not fetch the page.", 
            "what_it_is": "The title tag provides a brief summary of the content of the page and is displayed in search engine results and browser tabs.", 
            "how_to_fix": "Ensure the URL is correct and the website is accessible.",
            "audit_name": "Title Tag Audit"
        }

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

# <><><><><><><> START OF FUNCTION MD <><><><><><><>

def MD(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {
            "description": None, 
            "message": "Error: Could not fetch the page.", 
            "what_it_is": "The meta description provides a brief summary of the content of the page and is displayed in search engine results.", 
            "how_to_fix": "Ensure the URL is correct and the website is accessible.",
            "audit_name": "Meta Description Audit"
        }

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

# <><><><><><><> RUN AUDITS FUNCTION <><><><><><><>

def run_audits(url):
    return [TT(url), MD(url)]

# Streamlit App
st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    results = run_audits(url)
    for result in results:
        st.write("---")  # Line break
        st.subheader(result["audit_name"])  # Displaying the custom audit name

        if 'title' in result and result["title"]:
            st.info(f"**Title Tag Content:**\n```{result['title']}```")
            rating_tip = get_rating_and_tip(result["title"], "title tag")
            st.info(f"**Rating & Tip:** {rating_tip}")
        elif 'description' in result and result["description"]:
            st.info(f"**Meta Description Content:**\n```{result['description']}```")
            rating_tip = get_rating_and_tip(result["description"], "meta description")
            st.info(f"**Rating & Tip:** {rating_tip}")
        
        st.info(f"**Result:** {result['message']}\n\n*What it is:* {result['what_it_is']}\n\n*How to fix:* {result['how_to_fix']}")
