import streamlit as st
from bs4 import BeautifulSoup
import requests

# <><><><><><><> START OF FUNCTION TT <><><><><><><>

def TT(url):
    """
    Checks the title tag of the given page.
    - Determines if the title tag is missing.
    - Checks if the title tag's content is too long (more than 60 characters).
    - Checks if it's too short (less than 10 characters).
    
    Parameters:
    - url (str): The URL of the page to check.

    Returns:
    - dict: A dictionary with the title content and the result message.
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
    
    # Check if title is too long or too short
    if title_length > 60:
        return {"title": title_tag.text, "message": f"Fail: Title tag is too long ({title_length} characters)."}
    elif title_length < 10:
        return {"title": title_tag.text, "message": f"Fail: Title tag is too short ({title_length} characters)."}
    
    return {"title": title_tag.text, "message": "Pass: Title tag is within the recommended length."}

# <><><><><><><> END OF FUNCTION TT <><><><><><><>

def run_audits(url):
    """
    Runs all available audit functions on the given URL and returns results.
    
    Parameters:
    - url (str): The URL of the page to audit.

    Returns:
    - list: A list of results from all audit functions.
    """
    results = []

    # Run title tag check
    results.append(TT(url))

    # More audit functions can be added here in the future...

    return results

# Streamlit App
st.title("Single Page SEO Auditor")

# Input for the URL
url = st.text_input("Enter URL of the page to audit")

if url:
    results = run_audits(url)
    for result in results:
        if result["title"]:
            st.subheader("Title Tag Content")
            st.write(f"```{result['title']}```")
        st.subheader("Audit Result")
        st.markdown(f"**{result['message']}**")
