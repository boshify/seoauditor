import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai
from urllib.parse import urljoin
from urllib.parse import urlparse

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

# Define headers with a User-Agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

# Error handler for requests
def request_url(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None

def TT(url):
    response = request_url(url)
    if not response:
        return "Failed to fetch title", "Error retrieving title from URL"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "No Title Found"
    insights = ""
    
    if len(title) < 50:
        insights += "The title tag is shorter than the recommended 50-60 characters. Consider adding more descriptive keywords or phrases to improve its clarity."
    elif len(title) > 60:
        insights += "The title tag is longer than the recommended 50-60 characters. Consider shortening it while retaining its main message."
    else:
        insights += "The title tag is within the recommended length and seems well-optimized. Ensure it's relevant and unique to the content of the page."
    
    return title, insights

def MD(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    insights = ""

    if meta_description:
        desc = meta_description['content']
        
        if len(desc) < 150:
            insights += "The meta description is shorter than the recommended 150-160 characters. "
            insights += "Consider expanding it to provide a more comprehensive summary of the page. "
        elif len(desc) > 160:
            insights += "The meta description is longer than the recommended 150-160 characters. "
            insights += "Consider shortening it to make it concise. "
        
        ctas = ['learn more', 'discover', 'find out', 'get started', 'read on']
        if not any(cta in desc.lower() for cta in ctas):
            insights += "Consider adding a call to action in the meta description to entice users. "
        
        return desc, insights
    else:
        return None, "❌ Meta description is missing. Consider adding one to provide a brief summary of the page and improve click-through rates from search results."

def LinkingAudit(url):
    try:
        response = request_url(url)
        if not response:
            return [{"issue": "Error fetching URL", "solution": "Failed to retrieve content for linking audit"}]

        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('main') or soup.find('article') or soup.find('section') or soup

        structured_issues = []

        # Extract base URL
        base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
        
        links = [link for link in main_content.find_all('a', href=True) if not link['href'].startswith('#')]

        # Check for any other potential issues with links (for now, we're skipping relative links)
        # Add any other conditions as needed in the future.

        # If no issues found, return empty list
        if not structured_issues:
            return []

        return structured_issues
    except Exception as e:
        return [{"issue": "Unexpected error during link audit", "solution": str(e)}]



def AnchorTextAudit(url):
    try:
        response = request_url(url)
        if not response:
            return [("Error fetching URL", "Failed to retrieve content for anchor text audit")]

        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('main') or soup.find('article') or soup.find('section') or soup

        anchor_texts = [(a.get_text(strip=True), a['href']) for a in main_content.find_all('a', href=True) if a.get_text(strip=True)]
        generic_texts = ["click here", "read more", "here", "link", "more"]

        issues = []
        solutions = []

        for text, href in anchor_texts:
            if text.lower() in generic_texts:
                issues.append(f"Link: {href} | Anchor Text: '{text}'")
                solutions.append("Replace with more descriptive text that provides context about the content it links to.")

        # If there are fewer than 3 issues, add generic recommendations
        while len(issues) < 3 and anchor_texts:
            text, href = anchor_texts.pop(0)
            issues.append(f"Link: {href} | Anchor Text: '{text}'")
            solutions.append("Consider revising to be more specific or to avoid potential over-optimization.")

        if not issues:
            return ["No Issues Found"], ["All anchor texts on the page seem well-optimized."]

        return issues, solutions
    except Exception as e:
        return [("Unexpected error during anchor text audit", str(e))]






def get_pagespeed_insights(url):
    API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    API_KEY = st.secrets["pagespeed_api_key"]
    
    params = {
        "url": url,
        "key": API_KEY
    }
    
    response = requests.get(API_ENDPOINT, params=params, headers=HEADERS)
    data = response.json()
    
    return data

def analyze_pagespeed_data(data):
    crux_metrics = {}
    lighthouse_metrics = {}

    if 'loadingExperience' in data and 'metrics' in data['loadingExperience']:
        metrics = data['loadingExperience']['metrics']
        if 'FIRST_CONTENTFUL_PAINT_MS' in metrics:
            crux_metrics['First Contentful Paint'] = metrics['FIRST_CONTENTFUL_PAINT_MS']['category']
        if 'FIRST_INPUT_DELAY_MS' in metrics:
            crux_metrics['First Input Delay'] = metrics['FIRST_INPUT_DELAY_MS']['category']

    if 'lighthouseResult' in data and 'audits' in data['lighthouseResult']:
        audits = data['lighthouseResult']['audits']
        
        lighthouse_keys = {
            'First Contentful Paint': 'first-contentful-paint',
            'Speed Index': 'speed-index',
            'Time To Interactive': 'interactive',
            'First Meaningful Paint': 'first-meaningful-paint',
            'First CPU Idle': 'first-cpu-idle',
            'Estimated Input Latency': 'estimated-input-latency'
        }
        
        for display_key, audit_key in lighthouse_keys.items():
            if audit_key in audits and 'displayValue' in audits[audit_key]:
                lighthouse_metrics[display_key] = audits[audit_key]['displayValue']

    return crux_metrics, lighthouse_metrics

st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        with st.expander("🏷️ Title Tag Audit"):
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            if title_insights:
                st.write(f"**Recommendations:** {title_insights}")

        with st.expander("📝 Meta Description Audit"):
            meta_desc, meta_desc_insights = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
                if meta_desc_insights:
                    st.write(f"**Recommendations:** {meta_desc_insights}")
            else:
                st.write(meta_desc_insights)

        with st.expander("🔗 Linking Audit"):
            linking_issues = LinkingAudit(url)
            if linking_issues:
                for issue_data in linking_issues:
                    st.write("**Issue:**", issue_data["issue"])
                    st.write("**Solution:**", issue_data["solution"])
                    st.write("---")
            else:
                st.write("No internal linking issues found.")

        with st.expander("⚓ Anchor Text Audit"):
            issues, solutions = AnchorTextAudit(url)
            if issues:
                for issue, solution in zip(issues, solutions):
                    st.write("**Issue:**", issue)
                    st.write("**Solution:**", solution)
                    st.write("---")
            else:
                st.write("No anchor text issues found.")

        with st.expander("⚡ PageSpeed Insights"):
            pagespeed_data = get_pagespeed_insights(url)
            crux_metrics, lighthouse_metrics = analyze_pagespeed_data(pagespeed_data)
            
            st.write("## Chrome User Experience Report Results")
            for key, value in crux_metrics.items():
                st.write(f"**{key}:** {value}")
            
            st.write("## Lighthouse Results")
            for key, value in lighthouse_metrics.items():
                st.write(f"**{key}:** {value}")
