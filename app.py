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
    messages = [
        {"role": "system", "content": "You are an SEO expert."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message['content'].strip()

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
    response = request_url(url)
    if not response:
        return "Error retrieving meta description", "Failed to fetch content from URL"
    
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

def H1Audit(url):
    response = request_url(url)
    if not response:
        return "Error fetching URL", "Failed to retrieve content for H1 audit", ""

    soup = BeautifulSoup(response.text, 'html.parser')
    h1_elements = soup.find_all('h1')

    if not h1_elements:
        optimization = "H1 Missing"
        details = ("This page doesn't have an H1 heading. H1 headings are crucial for search engines to "
                   "understand the main topic of a webpage. They provide a clear and concise summary of the "
                   "content and improve the overall user experience by making the content more scannable and organized. "
                   "H1 headings also help search engines determine the relevance of a webpage to specific search queries, "
                   "increasing the chances of ranking higher in search engine results pages (SERPs).")
        recommendations = ("- Add an H1 heading to the page.\n"
                           "- Ensure the H1 heading accurately reflects the main topic of the webpage.\n"
                           "- Use relevant keywords in the H1 heading.\n"
                           "- Optimize the H1 heading to increase the chances of ranking higher in SERPs.\n"
                           "- Consider the overall on-page optimization efforts when adding the H1 heading.")
        return optimization, details, recommendations

    elif len(h1_elements) > 1:
        optimization = "Multiple H1s Found"
        details = ("Having multiple H1 headings on a page is not considered best practice from an SEO perspective. "
                   "H1 headings are used to indicate the main topic or focus of a page, and having multiple H1 headings "
                   "can confuse search engines and users about the primary content of the page.")
        h1_texts = [h1.get_text(strip=True) for h1 in h1_elements]
        primary_h1_suggestion = get_gpt_insights(f"Which should be the primary H1 heading among: {', '.join(h1_texts)}?")
        recommendations = (f"- Consolidate H1 headings: Choose one primary heading that best reflects the main topic "
                           f"or focus of the page. In this case, \"{primary_h1_suggestion}\" seems to be the most suitable "
                           "H1 heading. Remove any other H1 headings on the page.\n"
                           "- Use subheadings: Use appropriate subheadings such as H2, H3, etc., to organize the information.\n"
                           "- Optimize for keywords: Ensure the chosen H1 heading includes relevant keywords.\n"
                           "- Review content structure: Ensure the content flows well and supports the main H1 topic.\n"
                           "- Test and monitor: Monitor page performance and make adjustments based on data.")
        return optimization, details, recommendations

    else:
        optimization = "Single H1 Found"
        h1_text = h1_elements[0].get_text(strip=True)
        alternative_h1_suggestion = get_gpt_insights(f"Suggest an alternative SEO-optimized H1 heading for: {h1_text}")
        details = f"The page has an H1 heading: {h1_text}. It seems to be well-optimized."
        recommendations = f"Alternative H1 Suggestion for better optimization: {alternative_h1_suggestion}"
        return optimization, details, recommendations




def ImageAudit(url):
    response = request_url(url)
    if not response:
        return {"error": "Failed to retrieve content for image audit"}

    soup = BeautifulSoup(response.text, 'html.parser')
    img_elements = soup.find_all('img')

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

# The updated ImageAudit function is defined above, reverting the name change.



def LinkingAudit(url):
    try:
        response = request_url(url)
        if not response:
            return [{"issue": "Error fetching URL", "solution": "Failed to retrieve content for linking audit", "example": url}]
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup.find_all(['header', 'nav', 'footer']):
            element.extract()

        main_content = soup.find('main') or soup.find('article') or soup.find('section') or soup

        structured_issues = []
        seen_links = set()

        links = main_content.find_all('a', href=True)
        base_domain = urlparse(url).netloc

        for link in links:
            href = link['href']
            full_url = urljoin(url, href)

            # If link is internal and not checked before
            if base_domain in urlparse(full_url).netloc and full_url not in seen_links and not href.startswith('#'):
                seen_links.add(full_url)
                
                # Check if the link resolves correctly
                link_response = request_url(full_url)
                if not link_response or link_response.status_code >= 400:
                    structured_issues.append({
                        "issue": f"Broken internal link found: {full_url}",
                        "solution": f"Ensure the link is pointing to the correct location. Status Code: {link_response.status_code if link_response else 'Failed to fetch'}",
                        "example": href
                    })

        if not structured_issues:
            structured_issues.append({
                "issue": "No internal linking issues found.",
                "solution": "All internal links on the page seem to be working correctly."
            })

        return structured_issues
    except Exception as e:
        return [{"issue": "Unexpected error during linking audit", "solution": str(e), "example": url}]

# The modified LinkingAudit function is defined above. It checks the status code of every internal link and reports those that don't resolve correctly.




def AnchorTextAudit(url):
    try:
        response = request_url(url)
        if not response:
            return [("Error fetching URL", "Failed to retrieve content for anchor text audit")]

        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup.find_all(['header', 'nav', 'footer']):
            element.extract()

        main_content = soup.find('main') or soup.find('article') or soup.find('section') or soup
        anchor_texts = [(a.get_text(strip=True), a['href']) for a in main_content.find_all('a', href=True) if a.get_text(strip=True)]
        generic_texts = ["click here", "read more", "here", "link", "more"]

        links_to_improve = []
        recommended_anchor_texts = []

        for text, href in anchor_texts:
            if text.lower() in generic_texts:
                links_to_improve.append(f"Link: {href} | Anchor Text: '{text}'")
                gpt_suggestion = get_gpt_insights(f"Suggest a better anchor text for a link pointing to: {href}")
                recommended_anchor_texts.append(gpt_suggestion)

        while len(links_to_improve) < 3 and anchor_texts:
            text, href = anchor_texts.pop(0)
            links_to_improve.append(f"Link: {href} | Anchor Text: '{text}'")
            gpt_suggestion = get_gpt_insights(f"Suggest a better anchor text for a link pointing to: {href}")
            recommended_anchor_texts.append(gpt_suggestion)

        if not links_to_improve:
            return ["No Links to Improve Found"], ["All anchor texts on the page seem well-optimized."]

        return links_to_improve, recommended_anchor_texts
    except Exception as e:
        return [("Unexpected error during anchor text audit", str(e))]

# The modified AnchorTextAudit function is defined above. It now uses the requested wording for the anchor text audit section.


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

        with st.expander("🔖 H1 Heading Audit"):
            optimization, details, recommendations = H1Audit(url)
            st.write(f"**Optimization:** {optimization}")
            st.write(f"**Details:** {details}")
            st.write(f"**Recommendations:** {recommendations}")

        with st.expander("🖼️ Image Audit"):
            image_audit_results = ImageAudit(url)

            # ALT Attributes section
            st.write("**ALT Attributes**")
            if image_audit_results["missing_alt"][0]:
                st.write(f"**Images without ALT attributes:**")
                for img_src in image_audit_results["missing_alt"][0]:
                    st.write(f"- {img_src}")
                st.write(image_audit_results["missing_alt"][1])
                st.write("**Recommended ALT Texts:**")
                for img_src, alt_suggestion in image_audit_results["missing_alt"][2]:
                    st.write(f"- {img_src}: {alt_suggestion}")

            # Existing ALT attributes
            st.write("**Existing ALT Attributes Analysis**")
            for img_src, alt_text in image_audit_results["existing_alt"][0]:
                st.write(f"Image: {img_src} | Current ALT: {alt_text}")
            st.write(image_audit_results["existing_alt"][1])
            st.write("**Improved ALT Texts:**")
            for img_src, improved_alt in image_audit_results["existing_alt"][2]:
                st.write(f"- {img_src}: {improved_alt}")

            # Broken Images section
            st.write("**Broken Images**")
            if image_audit_results["broken_imgs"][0]:
                st.write(f"**Broken Images:**")
                for img_src in image_audit_results["broken_imgs"][0]:
                    st.write(f"- {img_src}")
                st.write(image_audit_results["broken_imgs"][1])

            # Descriptive Image Filenames
            st.write("**Descriptive Image Filenames**")
            if image_audit_results["non_descriptive_names"][0]:
                st.write(f"**Images with non-descriptive filenames:**")
                for img_src in image_audit_results["non_descriptive_names"][0]:
                    st.write(f"- {img_src}")
                st.write(image_audit_results["non_descriptive_names"][1])
                st.write("**Improved Filenames:**")
                for img_src, improved_name in image_audit_results["non_descriptive_names"][2]:
                    st.write(f"- {img_src}: {improved_name}")

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
