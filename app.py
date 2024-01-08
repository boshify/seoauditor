import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai
from urllib.parse import urljoin, urlparse

# Initialize OpenAI with API key from Streamlit's secrets
openai.api_key = st.secrets["openai_api_key"]

# Define headers with a User-Agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

def request_url(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None

def get_gpt_insights(prompt):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()

    except openai.OpenAIError as e:
        st.error(f"OpenAI API returned an error: {e}")
        return ""

def ImageAudit(url):
    response = request_url(url)
    if not response:
        return {"error": "Failed to retrieve content for image audit"}

    soup = BeautifulSoup(response.text, 'html.parser')
    img_elements = [img for img in soup.find_all('img') if img.get('src')]

    missing_alt = []
    existing_alt = []
    broken_imgs = []
    non_descriptive_names = []

    base_domain = urlparse(url).netloc

    for img in img_elements:
        # Check for missing alt attributes
        if not img.get('alt'):
            missing_alt.append(urljoin(url, img['src']))
        else:
            existing_alt.append((urljoin(url, img['src']), img['alt']))

        # Check for internal broken images
        img_src = urljoin(url, img['src'])
        if base_domain in urlparse(img_src).netloc:
            img_response = request_url(img_src)
            if not img_response:
                broken_imgs.append(img_src)

        # Non-descriptive filenames will be processed later (after the loop)
        img_name = urlparse(img['src']).path.split('/')[-1]
        if len(img_name.split('-')) <= 1:
            non_descriptive_names.append(img_src)

    # Recommendations for missing alt attributes
    alt_recommendations = []
    for img_src in missing_alt:
        img_name = urlparse(img_src).path.split('/')[-1]
        alt_suggestion = get_gpt_insights(f"Suggest an alt text for the image with filename: {img_name}")
        alt_recommendations.append((img_src, alt_suggestion))

    # Improved alt text for existing alt attributes
    improved_alt_texts = []
    for img_src, alt_text in existing_alt:
        improved_alt_suggestion = get_gpt_insights(f"Suggest a better alt text for the image with current alt text: {alt_text}")
        improved_alt_texts.append((img_src, improved_alt_suggestion))

    # Improved filenames for non-descriptive names
    improved_filenames = []
    for img_src in non_descriptive_names:
        img_name = urlparse(img_src).path.split('/')[-1]
        filename_suggestion = get_gpt_insights(f"Suggest a more descriptive filename for the image with current name: {img_name}")
        improved_filenames.append((img_src, filename_suggestion))

    return {
        "missing_alt": (missing_alt, "Images should have alt attributes for accessibility and SEO.", alt_recommendations),
        "existing_alt": (existing_alt, "Checking the descriptiveness of existing alt texts.", improved_alt_texts),
        "broken_imgs": (broken_imgs, "Broken images can lead to poor user experience.", "Consider re-uploading or fixing the source of the broken images."),
        "non_descriptive_names": (non_descriptive_names, "Descriptive image filenames can help with image SEO.", improved_filenames)
    }

# Streamlit app layout
st.title("Image SEO Auditor")
url = st.text_input("Enter URL of the page to audit images")

if url:
    with st.spinner("Analyzing images..."):
        image_audit_results = ImageAudit(url)
        for key, value in image_audit_results.items():
            st.write(f"**{value[1]}**")
            if isinstance(value[2], list):
                for img, suggestion in value[2]:
                    st.write(f"Image: {img}")
                    st.write(f"Suggestion: {suggestion}")
