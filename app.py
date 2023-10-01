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

    # Extract internal links within the main content
    internal_links = [a['href'] for a in main_content.find_all('a') if a['href'].startswith(url)]
    
    num_links = len(internal_links)
    word_count = len(main_content.text.split())

    # Assess the number of links based on content length
    recommended_links = word_count // 250  # One link per 250 words as a basic heuristic

    if num_links < recommended_links:
        issue = f"There are only {num_links} internal links in a content of {word_count} words."
        solution = f"It's recommended to have approximately one internal link every 250 words. Consider adding more relevant internal links."
        example = "For instance, if discussing 'SEO strategies', link to an article on your site that delves deeper into that topic."
    elif num_links > recommended_links * 2:  # Heuristic: more than twice the recommended links might be excessive
        issue = f"There are {num_links} internal links in a content of {word_count} words."
        solution = f"Too many links can overwhelm readers and look spammy to search engines. Consider reducing the number of links."
        example = "If multiple links point to the same destination, consider consolidating them."
    else:
        issue = "The number of internal links seems appropriate for the content length."
        solution = "Maintain this balanced approach to internal linking."
        example = ""

    return issue, solution, example

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
