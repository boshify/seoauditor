import streamlit as st
from bs4 import BeautifulSoup
import requests

# <><><><><><><> START OF FUNCTION TT <><><><><><><>

def TT(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {"title": None, "message": "Error: Could not fetch the page.", "what_it_is": "The title tag provides a brief summary of the content of the page and is displayed in search engine results and browser tabs.", "how_to_fix": "Ensure the URL is correct and the website is accessible."}

    soup = BeautifulSoup(response.content, 'html.parser')
    title_tag = soup.find('title')
    
    result = {
        "title": title_tag.text if title_tag else None,
        "message": "",
        "what_it_is": "The title tag provides a brief summary of the content of the page and is displayed in search engine results and browser tabs.",
        "how_to_fix": ""
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
        return {"description": None, "message": "Error: Could not fetch the page.", "what_it_is": "The meta description provides a brief summary of the content of the page and is displayed in search engine results.", "how_to_fix": "Ensure the URL is correct and the website is accessible."}

    soup = BeautifulSoup(response.content, 'html.parser')
    meta_description = soup.find('meta', attrs={"name": "description"})
    
    result = {
        "description": meta_description['content'] if meta_description else None,
        "message": "",
        "what_it_is": "The meta description provides a brief summary of the content of the page and is displayed in search engine results.",
        "how_to_fix": ""
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
        if 'title' in result and result["title"]:
            st.subheader("Title Tag Content")
            st.info(f"```{result['title']}```")
        elif 'description' in result and result["description"]:
            st.subheader("Meta Description Content")
            st.info(f"```{result['description']}```")
        
        st.subheader("Audit Result")
        st.info(f"**{result['message']}**\n\n*What it is:* {result['what_it_is']}\n\n*How to fix:* {result['how_to_fix']}")
