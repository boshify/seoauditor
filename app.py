import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai
from urllib.parse import urljoin

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

# ------------------------------ OpenAI GPT-3 Function ------------------------------
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

# ------------------------------ Title Tag Audit Function ------------------------------
def TT(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string
    insights = ""
    
    # Check title length
    if len(title) < 50:
        insights += "The title tag is shorter than the recommended 50-60 characters. "
        insights += "Consider adding more descriptive keywords or phrases to improve its clarity. "
    elif len(title) > 60:
        insights += "The title tag is longer than the recommended 50-60 characters. "
        insights += "Consider shortening it while retaining its main message. "
    else:
        insights += "The title tag is within the recommended length and seems well-optimized. "
        insights += "Ensure it's relevant and unique to the content of the page."
    
    return title, insights

# ------------------------------ Meta Description Audit Function ------------------------------
def MD(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    insights = ""

    if meta_description:
        desc = meta_description['content']
        
        # Check meta description length
        if len(desc) < 150:
            insights += "The meta description is shorter than the recommended 150-160 characters. "
            insights += "Consider expanding it to provide a more comprehensive summary of the page. "
        elif len(desc) > 160:
            insights += "The meta description is longer than the recommended 150-160 characters. "
            insights += "Consider shortening it to make it concise. "
        
        # Check for a call to action
        ctas = ['learn more', 'discover', 'find out', 'get started', 'read on']
        if not any(cta in desc.lower() for cta in ctas):
            insights += "Consider adding a call to action in the meta description to entice users. "
        
        return desc, insights
    else:
        return None, "❌ Meta description is missing. Consider adding one to provide a brief summary of the page and improve click-through rates from search results."

# ------------------------------ Linking Audit Function ------------------------------
def validate_link(base_url, href):
    # Convert relative URLs to absolute URLs
    full_url = urljoin(base_url, href)
    
    try:
        # Use a HEAD request to get the status code without downloading the entire page
        response = requests.head(full_url, allow_redirects=True, timeout=5)
        
        # If status code indicates client or server error, return it
        if 400 <= response.status_code <= 599:
            return response.status_code
    except requests.RequestException:
        # If there's a request exception, consider the link as broken
        return 503  # Service Unavailable as a generic error
    
    return None

def LinkingAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')

    if not main_content:
        main_content = soup.find('article') or soup.find('section') or soup  # Default to entire soup if none found

    structured_issues = []

    links = main_content.find_all('a')
    for link in links:
        href = link.get('href')
        status_code = validate_link(url, href)
        if status_code:
            issue_prompt = f"Analyze link with status {status_code}: {href}"
            insights = get_gpt_insights(issue_prompt)
        
            structured_issues.append({
                "issue": insights,
                "solution": get_gpt_insights(f"Provide a solution for the link issue: {href}"),
                "example": get_gpt_insights(f"Provide an example solution for the link issue: {href}")
            })

    return structured_issues

# ------------------------------ Anchor Text Audit Function ------------------------------
def AnchorTextAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')

    if not main_content:
        main_content = soup.find('article') or soup.find('section') or soup  # Default to entire soup if none found

    anchor_texts = [a.string for a in main_content.find_all('a') if a.string]
    generic_texts = ["click here", "read more", "here", "link", "more"]

    issues = [text for text in anchor_texts if text.lower() in generic_texts]
    solutions = [get_gpt_insights(f"Provide a solution for generic anchor text: {text}") for text in issues]
    examples = [get_gpt_insights(f"Provide an example solution for generic anchor text: {text}") for text in issues]

    return issues, solutions, examples

# ------------------------------ PageSpeed Insights Functions ------------------------------
def get_pagespeed_insights(url):
    API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    API_KEY = st.secrets["pagespeed_api_key"]  # Assuming you added it to secrets.toml as "pagespeed_api_key"
    
    params = {
        "url": url,
        "key": API_KEY
    }
    
    response = requests.get(API_ENDPOINT, params=params)
    data = response.json()
    
    return data

def analyze_pagespeed_data(data):
    crux_metrics = {
        "First Contentful Paint": data['loadingExperience']['metrics']['FIRST_CONTENTFUL_PAINT_MS']['category'],
        "First Input Delay": data['loadingExperience']['metrics']['FIRST_INPUT_DELAY_MS']['category']
    }

    lighthouse_metrics = {
        'First Contentful Paint': data['lighthouseResult']['audits']['first-contentful-paint']['displayValue'],
        'Speed Index': data['lighthouseResult']['audits']['speed-index']['displayValue'],
        'Time To Interactive': data['lighthouseResult']['audits']['interactive']['displayValue'],
        'First Meaningful Paint': data['lighthouseResult']['audits']['first-meaningful-paint']['displayValue'],
        'First CPU Idle': data['lighthouseResult']['audits']['first-cpu-idle']['displayValue'],
        'Estimated Input Latency': data['lighthouseResult']['audits']['estimated-input-latency']['displayValue']
    }

    return crux_metrics, lighthouse_metrics

# ------------------------------ Streamlit UI Rendering ------------------------------
st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        # Title Tag Audit
        with st.expander("🏷️ Title Tag Audit"):
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            if title_insights:
                st.write(f"**Recommendations:** {title_insights}")

        # Meta Description Audit
        with st.expander("📝 Meta Description Audit"):
            meta_desc, meta_desc_insights = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
                if meta_desc_insights:
                    st.write(f"**Recommendations:** {meta_desc_insights}")
            else:
                st.write(meta_desc_insights)

        # Linking Audit
        with st.expander("🔗 Linking Audit"):
            linking_issues = LinkingAudit(url)
            for issue_data in linking_issues:
                st.write("**Issue:**", issue_data["issue"])
                st.write("**Solution:**", issue_data["solution"])
                st.write("**Example:**", issue_data["example"])
                st.write("---")  # Adds a horizontal line for separation

        # Anchor Text Audit
        with st.expander("⚓ Anchor Text Audit"):
            issues, solutions, examples = AnchorTextAudit(url)
            for issue, solution, example in zip(issues, solutions, examples):
                st.write("**Issue:**", issue)
                st.write("**Solution:**", solution)
                st.write("**Example:**", example)
                st.write("---")  # Adds a horizontal line for separation

        # PageSpeed Insights Audit
        with st.expander("⚡ PageSpeed Insights"):
            pagespeed_data = get_pagespeed_insights(url)
            crux_metrics, lighthouse_metrics = analyze_pagespeed_data(pagespeed_data)
            
            st.write("## Chrome User Experience Report Results")
            for key, value in crux_metrics.items():
                st.write(f"**{key}:** {value}")
            
            st.write("## Lighthouse Results")
            for key, value in lighthouse_metrics.items():
                st.write(f"**{key}:** {value}")
