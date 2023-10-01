import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

def get_gpt_insights(prompt):
    messages = [
        {"role": "system", "content": "You are an SEO expert."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    return response.choices[0].message['content'].strip()

def TT(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string
    insights = get_gpt_insights(f"Analyze the title tag: {title}")
    return title, insights

def MD(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    insights = None
    if meta_description:
        insights = get_gpt_insights(f"Analyze the meta description: {meta_description['content']}")
        return meta_description['content'], insights
    else:
        return None, "❌ Meta description is missing."

def LinkingAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')  # Extracting main content
    
    # If no <main> tag, try to infer main content
    if not main_content:
        main_content = soup.find('article') or soup.find('section')

    issues = []
    
    # Extract all links within the main content
    links = main_content.find_all('a')

    # Check for too many on-page links
    if len(links) > 100: # Here, I'm using 100 as a threshold, which can be adjusted.
        issues.append("This page has too many on-page links.")

    for link in links:
        href = link.get('href')
        # Check for long URLs
        if len(href) > 2000: # 2000 is a heuristic.
            issues.append(f"Link URL on this page is too long: {href}")

        # Check for non-descriptive anchor text
        anchor_text = link.string
        generic_texts = ["click here", "read more", "here", "link", "more"]
        if anchor_text and anchor_text.lower() in generic_texts:
            issues.append(f"Link on this page has non-descriptive anchor text: {anchor_text}")

        # Check for mixed content (HTTPS page linking to HTTP)
        if url.startswith('https:') and href.startswith('http:'):
            issues.append(f"Links on this HTTPS page lead to an HTTP page: {href}")

        # Check status of external links
        if not href.startswith(url):
            try:
                ext_response = requests.head(href, allow_redirects=True, timeout=5)
                if ext_response.status_code == 403:
                    issues.append(f"Links to external page {href} returned a 403 HTTP status code.")
                if ext_response.status_code == 404:
                    issues.append(f"External link on this page is broken: {href}")
            except requests.RequestException:
                issues.append(f"Couldn't access the external link: {href}")

    # Check external JS and CSS files
    js_files = main_content.find_all('script', src=True)
    css_files = main_content.find_all('link', rel='stylesheet', href=True)

    for resource in js_files + css_files:
        href = resource.get('src') or resource.get('href')
        try:
            ext_response = requests.head(href, allow_redirects=True, timeout=5)
            if ext_response.status_code == 404:
                issues.append(f"Broken external {resource.name.upper()} file linked from this page: {href}")
        except requests.RequestException:
            issues.append(f"Couldn't access the external {resource.name.upper()} file: {href}")

    # Check external images
    img_tags = main_content.find_all('img', src=True)
    for img_tag in img_tags:
        href = img_tag.get('src')
        try:
            ext_response = requests.head(href, allow_redirects=True, timeout=5)
            if ext_response.status_code == 404:
                issues.append(f"External image linked from this page is broken: {href}")
        except requests.RequestException:
            issues.append(f"Couldn't access the external image: {href}")

    # You can further add checks for hreflang links or any other specific requirements here.
    
    return issues

def AnchorTextAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')  # Extracting main content
    
    # If no <main> tag, try to infer main content
    if not main_content:
        main_content = soup.find('article') or soup.find('section')

    # Extract anchor texts within the main content
    anchor_texts = [a.string for a in main_content.find_all('a') if a.string]

    generic_texts = ["click here", "read more", "here", "link", "more"]
    
    issues, solutions, examples = [], [], []
    
    for text in anchor_texts:
        if text.lower() in generic_texts:
            issues.append(f"The anchor text '{text}' is too generic.")
            solutions.append("Use more descriptive anchor texts.")
            examples.append(f"Instead of '{text}', consider using 'Discover our SEO strategies' or 'Learn more about our services'.")

    return issues, solutions, examples

st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        # Title Tag Audit
        with st.expander("🏷️ Title Tag Audit"):
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            st.write(f"**GPT Insights:** {title_insights}")

        # Meta Description Audit
        with st.expander("📝 Meta Description Audit"):
            meta_desc, meta_desc_insights = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
                st.write(f"**GPT Insights:** {meta_desc_insights}")
            else:
                st.write(meta_desc_insights)

        # Linking Audit
        with st.expander("🔗 Linking Audit"):
            issue, solution, example = LinkingAudit(url)
            st.write(issue)
            st.write(solution)
            st.write(example)

        # Anchor Text Audit
        with st.expander("⚓ Anchor Text Audit"):
            issues, solutions, examples = AnchorTextAudit(url)
            for issue, solution, example in zip(issues, solutions, examples):
                st.write(issue)
                st.write(solution)
                st.write(example)
