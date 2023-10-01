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
    main_content = soup.find('main')

    if not main_content:
        main_content = soup.find('article') or soup.find('section')

    structured_issues = []

    links = main_content.find_all('a')
    if len(links) > 100:
        structured_issues.append({
            "issue": "This page has too many on-page links.",
            "solution": "Consider reducing the number of links for better user experience.",
            "example": "If multiple links point to the same destination, consider consolidating them."
        })

    for link in links:
        href = link.get('href')
        if len(href) > 2000:
            structured_issues.append({
                "issue": f"Link URL on this page is too long: {href}",
                "solution": "Consider using URL shorteners or restructuring the URL.",
                "example": "Avoid using unnecessary parameters or overly descriptive paths."
            })

        anchor_text = link.string
        generic_texts = ["click here", "read more", "here", "link", "more"]
        if anchor_text and anchor_text.lower() in generic_texts:
            structured_issues.append({
                "issue": f"Link on this page has non-descriptive anchor text: {anchor_text}",
                "solution": "Use more descriptive anchor texts.",
                "example": f"Instead of '{anchor_text}', consider using 'Discover our SEO strategies' or 'Learn more about our services'."
            })

        if url.startswith('https:') and href.startswith('http:'):
            structured_issues.append({
                "issue": f"Links on this HTTPS page lead to an HTTP page: {href}",
                "solution": "Update links to use HTTPS to ensure secure content delivery.",
                "example": "Replace 'http://' with 'https://' in the link if the destination supports it."
            })

        if not href.startswith(url):
            try:
                ext_response = requests.head(href, allow_redirects=True, timeout=5)
                if ext_response.status_code == 403:
                    structured_issues.append({
                        "issue": f"Links to external page {href} returned a 403 HTTP status code.",
                        "solution": "Check the external link's access permissions.",
                        "example": "Ensure you are not linking to private or restricted content."
                    })
                if ext_response.status_code == 404:
                    structured_issues.append({
                        "issue": f"External link on this page is broken: {href}",
                        "solution": "Update or remove the broken link.",
                        "example": "Link to an updated resource or related content."
                    })
            except requests.RequestException:
                structured_issues.append({
                    "issue": f"Couldn't access the external link: {href}",
                    "solution": "Ensure the external link is correct and accessible.",
                    "example": "Verify the link's URL and destination."
                })

    js_files = main_content.find_all('script', src=True)
    css_files = main_content.find_all('link', rel='stylesheet', href=True)
    for resource in js_files + css_files:
        href = resource.get('src') or resource.get('href')
        try:
            ext_response = requests.head(href, allow_redirects=True, timeout=5)
            if ext_response.status_code == 404:
                structured_issues.append({
                    "issue": f"Broken external {resource.name.upper()} file linked from this page: {href}",
                    "solution": "Update the link to the external resource.",
                    "example": "Ensure you are linking to the correct and updated {resource.name.upper()} file."
                })
        except requests.RequestException:
            structured_issues.append({
                "issue": f"Couldn't access the external {resource.name.upper()} file: {href}",
                "solution": "Ensure the link to the external {resource.name.upper()} file is correct.",
                "example": "Verify the resource's URL and accessibility."
            })

    img_tags = main_content.find_all('img', src=True)
    for img_tag in img_tags:
        href = img_tag.get('src')
        try:
            ext_response = requests.head(href, allow_redirects=True, timeout=5)
            if ext_response.status_code == 404:
                structured_issues.append({
                    "issue": f"External image linked from this page is broken: {href}",
                    "solution": "Update the link to the external image.",
                    "example": "Ensure you are linking to the correct and accessible image."
                })
        except requests.RequestException:
            structured_issues.append({
                "issue": f"Couldn't access the external image: {href}",
                "solution": "Ensure the link to the external image is correct.",
                "example": "Verify the image's URL and accessibility."
            })

    return structured_issues

def AnchorTextAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')

    if not main_content:
        main_content = soup.find('article') or soup.find('section') or soup  # Default to entire soup

    anchor_texts = [a.string for a in main_content.find_all('a') if a.string]
    generic_texts = ["click here", "read more", "here", "link", "more"]
    issues, solutions, examples = [], [], []
    
    # Check for generic anchor texts
    for text in anchor_texts:
        if text.lower() in generic_texts:
            issues.append(f"The anchor text '{text}' is too generic.")
            solutions.append("Use more descriptive anchor texts.")
            examples.append(f"Instead of '{text}', consider using 'Discover our SEO strategies' or 'Learn more about our services'.")

    # Check for overoptimized anchor texts
    from collections import Counter
    anchor_text_count = Counter(anchor_texts)
    for text, count in anchor_text_count.items():
        if count > 5:
            issues.append(f"The anchor text '{text}' is repeated {count} times. It might be overoptimized.")
            solutions.append("Diversify your anchor texts.")
            examples.append(f"Instead of using '{text}' multiple times, consider other variations or synonyms.")
    
    # Check for short anchor texts
    for text in anchor_texts:
        if len(text.split()) == 1:
            issues.append(f"The anchor text '{text}' is too short.")
            solutions.append("Use more descriptive anchor texts.")
            # Provide more specific examples based on the anchor text context
            if text.lower() == "linkedin":
                examples.append(f"Consider using 'Visit my LinkedIn profile'.")
            elif text.lower() == "newsletter":
                examples.append(f"Consider using 'Subscribe to our newsletter'.")
            else:
                examples.append(f"Expand on '{text}' to provide more context or detail.")
    
    # Check for long anchor texts
    for text in anchor_texts:
        if len(text.split()) > 8:
            issues.append(f"The anchor text '{text}' is too long and might not be user-friendly.")
            solutions.append("Shorten the anchor text while retaining its meaning.")
            examples.append(f"Consider a more concise version of '{text}'.")
    
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
            linking_issues = LinkingAudit(url)
            for issue_data in linking_issues:
                st.write("**Issue:**", issue_data["issue"])
                st.write("**Solution:**", issue_data["solution"])
                st.write("**Example:**", issue_data["example"])

        # Anchor Text Audit
        with st.expander("⚓ Anchor Text Audit"):
            issues, solutions, examples = AnchorTextAudit(url)
            for issue, solution, example in zip(issues, solutions, examples):
                st.write("**Issue:**", issue)
                st.write("**Solution:**", solution)
                st.write("**Example:**", example)
                st.write("---")  # Adds a horizontal line for separation

