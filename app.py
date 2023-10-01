import streamlit as st
from bs4 import BeautifulSoup
import requests

# <><><><><><><> START OF FUNCTION TT <><><><><><><>

def TT(url):
    """
    Checks the title tag of the given page.
    """
    # Fetch the content of the page
    response = requests.get(url)
    if response.status_code != 200:
        return {"title": None, "message": "Error: Could not fetch the page."}

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the title tag
    title_tag = soup.find('title')
    
    # Check if title tag is missing
    if not title_tag:
        return {"title": None, "message": "Fail: Title tag is missing."}
    
    title_length = len(title_tag.text)
    
    # Update to include "What it is" and "How to fix it" information
    result = {
        "title": title_tag.text,
        "message": "",
        "what_it_is": "The title tag provides a brief summary of the content of the page and is displayed in search engine results and browser tabs.",
        "how_to_fix": ""
    }

    if title_length > 60:
        result["message"] = f"Fail: Title tag is too long ({title_length} characters)."
        result["how_to_fix"] = "Reduce the length of the title tag to 60 characters or fewer."
    elif title_length < 10:
        result["message"] = f"Fail: Title tag is too short ({title_length} characters)."
        result["how_to_fix"] = "Increase the length of the title tag to at least 10 characters."
    else:
        result["message"] = "Pass: Title tag is within the recommended length."

    return result

# <><><><><><><> START OF FUNCTION MD <><><><><><><>

def MD(url):
    """
    Checks the meta description of the given page.
    """
    # Fetch the content of the page
    response = requests.get(url)
    if response.status_code != 200:
        return {"description": None, "message": "Error: Could not fetch the page."}

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the meta description tag
    meta_description = soup.find('meta', attrs={"name": "description"})
    
    # Check if meta description is missing
    if not meta_description or not meta_description.get('content'):
        return {"description": None, "message": "Fail: Meta description is missing."}
    
    description_length = len(meta_description['content'])
    
    # Update to include "What it is" and "How to fix it" information
    result = {
        "description": meta_description['content'],
        "message": "",
        "what_it_is": "The meta description provides a brief summary of the content of the page and is displayed in search engine results.",
        "how_to_fix": ""
    }

    if description_length > 160:
        result["message"] = f"Fail: Meta description is too long ({description_length} characters)."
        result["how_to_fix"] = "Reduce the length of the meta description to 160 characters or fewer."
    elif description_length < 50:
        result["message"] = f"Fail: Meta description is too short ({description_length} characters)."
        result["how_to_fix"] = "Increase the length of the meta description to at least 50 characters."
    else:
        result["message"] = "Pass: Meta description is within the recommended length."

    return result

# <><><><><><><> RUN AUDITS FUNCTION <><><><><><><>

def run_audits(url):
    results = []

    # Run title tag check
    results.append(TT(url))
    
    # Run meta description check
    results.append(MD(url))

    return results

# Streamlit App
st.title("Single Page SEO Auditor")

# Input for the URL
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
