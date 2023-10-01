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

def validate_link(href):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.head(href, headers=headers, allow_redirects=True, timeout=5)
        if response.status_code in [403, 405]:  # 403: Forbidden, 405: Method Not Allowed
            response = requests.get(href, headers=headers, allow_redirects=True, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None

def TT(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string
    insights = get_gpt_insights(f"Analyze title: {title}")
    return title, insights

def MD(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    
    if meta_description:
        desc = meta_description['content']
        insights = get_gpt_insights(f"Analyze meta description: {desc}")
        return desc, insights
    else:
        return None, "❌ Meta description is missing. Consider adding one."

def LinkingAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')

    if not main_content:
        main_content = soup.find('article') or soup.find('section')

    structured_issues = []

    links = main_content.find_all('a')
    for link in links:
        href = link.get('href')
        status_code = validate_link(href)
        if status_code:
            issue_prompt = f"Analyze link with status {status_code}: {href}"
        else:
            issue_prompt = f"Couldn't access the external link: {href}"
        insights = get_gpt_insights(issue_prompt)
        
        structured_issues.append({
            "issue": insights,
            "solution": get_gpt_insights(f"Provide a solution for the link issue: {href}"),
            "example": get_gpt_insights(f"Provide an example solution for the link issue: {href}")
        })

    return structured_issues

def AnchorTextAudit(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('main')

    if not main_content:
        main_content = soup.find('article') or soup.find('section')

    anchor_texts = [a.string for a in main_content.find_all('a') if a.string]
    issues, solutions, examples = [], [], []
    
    for text in anchor_texts:
        issues.append(get_gpt_insights(f"Analyze anchor text: {text}"))
        solutions.append(get_gpt_insights(f"Provide a solution for anchor text: {text}"))
        examples.append(get_gpt_insights(f"Provide an example solution for anchor text: {text}"))
    
    return issues, solutions, examples

st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    with st.spinner("Analyzing..."):
        # Title Tag Audit
        with st.expander("🏷️ Title Tag Audit"):
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            st.write(f"**Recommendations:** {title_insights}")

        # Meta Description Audit
        with st.expander("📝 Meta Description Audit"):
            meta_desc, meta_desc_insights = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
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
