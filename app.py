import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to crawl a webpage and return its source code
def fetch_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

# Check for duplicate title tags (for demonstration purposes, we're just checking if there's exactly one title tag)
def check_title_tags(soup):
    title_tags = soup.find_all('title')
    return "Pass" if len(title_tags) == 1 else "Fail"

def main():
    st.title("Single Page SEO Auditor")

    url = st.text_input("Enter the URL of the page to audit")

    if st.button("Audit"):
        if not url:
            st.warning("Please enter a URL.")
        else:
            content = fetch_page_content(url)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Title tag check
                title_check_result = check_title_tags(soup)
                st.write(f"Title Tag Check: {title_check_result}")

                # Here, you can add more checks as needed.

if __name__ == "__main__":
    main()
