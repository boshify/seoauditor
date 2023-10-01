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

# <><><><><><><> START OF FUNCTION MD <><><><><><><>

def MD(url):
    """
    Checks the meta description of the given page.
    - Determines if the meta description is missing.
    - Checks if the meta description's content is too long (more than 160 characters).
    - Checks if it's too short (less than 50 characters).
    
    Parameters:
    - url (str): The URL of the page to check.

    Returns:
    - dict: A dictionary with the meta description content and the result message.
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
    
    # Check if meta description is too long or too short
    if description_length > 160:
        return {"description": meta_description['content'], "message": f"Fail: Meta description is too long ({description_length} characters)."}
    elif description_length < 50:
        return {"description": meta_description['content'], "message": f"Fail: Meta description is too short ({description_length} characters)."}
    
    return {"description": meta_description['content'], "message": "Pass: Meta description is within the recommended length."}

# <><><><><><><> END OF FUNCTION MD <><><><><><><>

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
    
    # Run meta description check
    results.append(MD(url))

    # More audit functions can be added here in the future...

    return results

# Streamlit App
st.title("Single Page SEO Auditor")

# Input for the URL
url = st.text_input("Enter URL of the page to audit")

if url:
    results = run_audits(url)
    for result in results:
        if 'title' in result and result["title"]:
            st.subheader("Title Tag Content")
            st.write(f"```{result['title']}```")
        elif 'description' in result and result["description"]:
            st.subheader("Meta Description Content")
            st.write(f"```{result['description']}```")
        
        st.subheader("Audit Result")
        st.markdown(f"**{result['message']}**")
