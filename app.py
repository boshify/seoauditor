import streamlit as st
from bs4 import BeautifulSoup
import requests

# Progress bar messages
PROGRESS_MESSAGES = [
    "Initializing...",
    "Fetching website data...",
    "Analyzing title tag...",
    "Analyzing meta description...",
    "Checking links...",
    "Finalizing..."
]

def TT(soup):
    title_tag = soup.title.string if soup.title else None
    if not title_tag:
        return {
            "message": "No title tag found.",
            "what_it_is": "Analysis of the webpage title.",
            "how_to_fix": "Ensure the webpage has a <title> tag.",
            "audit_name": "Title Audit"
        }
    else:
        # Here, you can add more analysis on the title tag if needed
        return {
            "message": f"Title: {title_tag}",
            "what_it_is": "Analysis of the webpage title.",
            "how_to_fix": "Review the title for relevant keywords and appropriate length.",
            "audit_name": "Title Audit"
        }

def MD(soup):
    meta_description = soup.find('meta', attrs={'name': 'description'})
    content = meta_description['content'] if meta_description else None
    if not content:
        return {
            "message": "No meta description found.",
            "what_it_is": "Analysis of the webpage's meta description.",
            "how_to_fix": "Ensure the webpage has a meta description tag.",
            "audit_name": "Meta Description Audit"
        }
    else:
        # Here, you can add more analysis on the meta description if needed
        return {
            "message": f"Meta Description: {content}",
            "what_it_is": "Analysis of the webpage's meta description.",
            "how_to_fix": "Review the meta description for relevant keywords and appropriate length.",
            "audit_name": "Meta Description Audit"
        }

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

    error_links, long_links, broken_links, resource_as_link, img_links = [], [], [], [], []
    for link_element in visible_links:
        link = link_element['href']

        # Checking for relative links and converting them to absolute links
        if link.startswith("/"):
            link = url.rstrip("/") + link

        if len(link) > 200:
            long_links.append(link)
            continue

        try:
            r = requests.get(link, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                broken_links.append(f"{link} (status {r.status_code})")
        except Exception as e:
            error_links.append(f"{link} ({str(e)})")

        if link_element.name == "img":
            img_links.append(link)
            if not any(ext in link for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                resource_as_link.append(link)

    messages = []
    if error_links:
        messages.append("**Error accessing links:**\n- " + '\n- '.join(error_links))
    if long_links:
        messages.append("**Very long URLs:**\n- " + '\n- '.join(long_links))
    if broken_links:
        messages.append("**Broken links:**\n- " + '\n- '.join(broken_links))
    if len(visible_links) > 100:
        messages.append("**Note:** This page has too many on-page links.")
    if resource_as_link:
        messages.append("**Resources formatted as page links:**\n- " + '\n- '.join(resource_as_link))
    if img_links:
        messages.append("**Images as links:**\n- " + '\n- '.join(img_links))

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
        
        if msg == "Fetching website data...":
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
        elif msg == "Analyzing title tag...":
            title_results = TT(soup)
        elif msg == "Analyzing meta description...":
            meta_results = MD(soup)
        elif msg == "Checking links...":
            link_results = IL(url)

    # Display results
    for result in [title_results, meta_results, link_results]:
        st.write("---")
        st.subheader(result['audit_name'])
        st.markdown(result['message'])
        st.write("**What it is:**", result['what_it_is'])
        if 'how_to_fix' in result and result['how_to_fix']:
            st.write("**How to fix:**", result['how_to_fix'])
