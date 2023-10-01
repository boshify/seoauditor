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
    - str: A message indicating the result of the check.
    """
    # Fetch the content of the page
    response = requests.get(url)
    if response.status_code != 200:
        return "Error: Could not fetch the page."

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the title tag
    title_tag = soup.find('title')
    
    # Check if title tag is missing
    if not title_tag:
        return "Fail: Title tag is missing."
    
    title_length = len(title_tag.text)
    
    # Check if title is too long or too short
    if title_length > 60:
        return f"Fail: Title tag is too long ({title_length} characters)."
    elif title_length < 10:
        return f"Fail: Title tag is too short ({title_length} characters)."
    
    return "Pass: Title tag is within the recommended length."

# <><><><><><><> END OF FUNCTION TT <><><><><><><>

# Streamlit App
st.title("Single Page SEO Auditor")

# Input for the URL
url = st.text_input("Enter URL of the page to audit")

if url:
    if st.button("Check Title Tag"):
        result = TT(url)
        st.write(result)
