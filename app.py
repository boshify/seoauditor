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

def safe_request_url(target_url, method='GET'):
    try:
        if method.upper() == 'HEAD':
            response = requests.head(target_url, headers=HEADERS, allow_redirects=True)
        else:
            response = requests.get(target_url, headers=HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        st.warning(f"Error fetching URL: {e}")
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
    title = soup.title.string if soup.title else None
    insights = ""
    
    if title is None:
        return "No Title Found", "No title tag detected for the page."
    elif len(title) < 50:
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

def crawlability_insights(url):
    issues = []

    # Enhanced request function with error handling
    def safe_request_url(target_url):
        try:
            # Append the base URL if no scheme is provided
            if not urlparse(target_url).scheme:
                target_url = urljoin(url, target_url)
            response = request_url(target_url)
            return response
        except requests.RequestException as e:
            issues.append(("Error", f"Error fetching URL: {e}", "Ensure the URL is accessible and valid."))
            return None

    response = safe_request_url(url)
    if not response:
        return issues  # Return early if the main page can't be crawled

    soup = BeautifulSoup(response.text, 'html.parser')

    # CANON check (broken canonical link)
    canonical_link = soup.find("link", rel="canonical")
    if canonical_link and not safe_request_url(canonical_link['href']):
        issues.append(("CANON",
                       f"This page has a broken canonical link pointing to {canonical_link['href']}.",
                       "Ensure the canonical link points to a valid and accessible URL."))

    # JSCSS, JSCSSFILES, and JSCSSSIZE checks
    css_files = [link['href'] for link in soup.find_all('link', rel='stylesheet') if link.get('href')]
    js_files = [script['src'] for script in soup.find_all('script', src=True) if script.get('src')]
    broken_js_css = [link for link in css_files if not safe_request_url(link)] + [script for script in js_files if not safe_request_url(script)]

    if broken_js_css:
        issues.append(("JSCSS", 
                       f"Issues with broken internal JavaScript and CSS files: {', '.join(broken_js_css)}",
                       "Ensure all linked JS and CSS files are accessible."))

    num_files = len(css_files + js_files)
    total_js_css_size = sum([len(safe_request_url(link).text) for link in css_files + js_files if safe_request_url(link)])
    
    if num_files > 10:  # Assuming more than 10 files is too many
        issues.append(("JSCSSFILES", 
                       f"This page uses {num_files} JavaScript and CSS files, which is considered excessive.", 
                       "Consider combining and minifying JS and CSS files to reduce the number of HTTP requests."))

    if total_js_css_size > 1 * 1024 * 1024:  # Assuming more than 1MB of JS/CSS is too much
        issues.append(("JSCSSSIZE", 
                       f"The total size of JavaScript and CSS on this page is {total_js_css_size / (1024 * 1024):.2f}MB, which is considered too large.", 
                       "Optimize and compress JS and CSS files to improve page load time."))

    # LINKCRAWL check
    internal_links = [a['href'] for a in soup.find_all('a', href=True) if urlparse(url).netloc in urlparse(a['href']).netloc]
    non_crawlable_links = [link for link in internal_links if not safe_request_url(link)]
    if non_crawlable_links:
        issues.append(("LINKCRAWL",
                       f"Links on this page couldn't be crawled (incorrect URL formats): {', '.join(non_crawlable_links)}",
                       "Ensure all internal links on the page point to valid and accessible URLs."))

    # MINIFY check (simplified)
    unminified_files = [link for link in css_files + js_files if ".min." not in link]
    if unminified_files:
        issues.append(("MINIFY",
                       f"Issues with unminified JavaScript and CSS files: {', '.join(unminified_files)}",
                       "Minify the JS and CSS files to improve page load time."))

    return issues



def accessibility_insights(url):
    issues = []
    
    # Using a set to keep track of all URLs we've visited to detect loops
    visited_urls = set()

    # Make a HEAD request to the URL to check for redirects without downloading the entire content
    response = safe_request_url(url, method='HEAD')
    
    if not response:
        issues.append(("URLRES", "URL does not resolve.", "Ensure the URL is correct and the server is responsive."))
        return issues  # Return early if the URL doesn't resolve

    # Check for redirect chains and loops
    if len(response.history) > 1:
        for r in response.history:
            # If a URL appears more than once in the history, it's a loop
            if r.url in visited_urls:
                issues.append(("REDIRCHAIN", "Redirect chains and loops detected on this page.", f"The URL {r.url} was redirected to multiple times. Ensure redirects are set up correctly to avoid loops."))
                break
            visited_urls.add(r.url)

    # Check for temporary and permanent redirects
    if response.history:
        last_redirect = response.history[-1]
        if last_redirect.status_code == 301:
            issues.append(("PERMREDIR", "This URL has a permanent redirect.", f"The URL redirects permanently (301) to {response.url}. Ensure this is intended and update references to the original URL if necessary."))
        else:
            issues.append(("TEMPREDIR", "This URL has a temporary redirect.", f"The URL redirects temporarily ({last_redirect.status_code}) to {response.url}. Ensure this is intended, as temporary redirects might not pass link equity in the same way permanent redirects do."))

    # General redirect issue check (if any of the above conditions were triggered)
    if any(issue[0] in ["TEMPREDIR", "PERMREDIR", "REDIRCHAIN"] for issue in issues):
        issues.append(("REDIR", "This URL has a redirect issue.", "Review the specific redirect issues listed above and rectify as necessary."))

    return issues








st.title("Single Page SEO Auditor")
url = st.text_input("Enter URL of the page to audit")

if url:
    progress = st.progress(0)
    progress_step = 1.0 / 9  # Based on the number of audits
    status = st.empty()  # Placeholder for status messages

    with st.spinner("Analyzing..."):
        col1, col2 = st.columns(2)  # Creating two columns

        status.text("Analyzing Title Tag...")
        with col1.expander("🏷️ Title Tag Audit"):
            title, title_insights = TT(url)
            st.write(f"**Title Tag Content:** {title}")
            if title_insights:
                st.write(f"**Recommendations:** {title_insights}")
        progress.progress(progress_step)

        status.text("Analyzing Meta Description...")
        with col1.expander("📝 Meta Description Audit"):
            meta_desc, meta_desc_insights = MD(url)
            if meta_desc:
                st.write(f"**Meta Description Content:** {meta_desc}")
                if meta_desc_insights:
                    st.write(f"**Recommendations:** {meta_desc_insights}")
            else:
                st.write(meta_desc_insights)
        progress.progress(2 * progress_step)

        status.text("Auditing H1 Headings...")
        with col1.expander("🔖 H1 Heading Audit"):
            optimization, details, recommendations = H1Audit(url)
            st.write(f"**Optimization:** {optimization}")
            st.write(f"**Details:** {details}")
            st.write(f"**Recommendations:** {recommendations}")
        progress.progress(3 * progress_step)

        status.text("Auditing Images...")
        with col1.expander("🖼️ Image Audit"):
            image_audit_results = ImageAudit(url)
            for key, value in image_audit_results.items():
                st.write(f"**{value[1]}**")
                if isinstance(value[2], list):
                    for img, suggestion in value[2]:
                        st.write(f"Image: {img}")
                        st.write(f"Suggestion: {suggestion}")
                else:
                    st.write(value[2])
                st.write("---")
        progress.progress(4 * progress_step)

        status.text("Analyzing Linking...")
        with col2.expander("🔗 Linking Audit"):
            linking_issues = LinkingAudit(url)
            if linking_issues:
                for issue_data in linking_issues:
                    st.write("**Issue:**", issue_data["issue"])
                    st.write("**Solution:**", issue_data["solution"])
                    st.write("---")
            else:
                st.write("No internal linking issues found.")
        progress.progress(5 * progress_step)

        status.text("Analyzing Anchor Texts...")
        with col2.expander("⚓ Anchor Text Audit"):
            issues, solutions = AnchorTextAudit(url)
            if issues:
                for issue, solution in zip(issues, solutions):
                    st.write("**Issue:**", issue)
                    st.write("**Solution:**", solution)
                    st.write("---")
            else:
                st.write("No anchor text issues found.")
        progress.progress(6 * progress_step)

        status.text("Fetching PageSpeed Insights...")
        with col2.expander("⚡ PageSpeed Insights"):
            pagespeed_data = get_pagespeed_insights(url)
            crux_metrics, lighthouse_metrics = analyze_pagespeed_data(pagespeed_data)
            st.write("## Chrome User Experience Report Results")
            for key, value in crux_metrics.items():
                st.write(f"**{key}:** {value}")
            st.write("## Lighthouse Results")
            for key, value in lighthouse_metrics.items():
                st.write(f"**{key}:** {value}")
        progress.progress(7 * progress_step)

        status.text("Analyzing Crawlability...")
        with col2.expander("🕷️ Crawlability Insights"):
            crawl_issues = crawlability_insights(url)
            if crawl_issues:
                for issue_code, issue_description, solution in crawl_issues:
                    st.write(f"**Issue ({issue_code}):** {issue_description}")
                    st.write(f"**Solution:** {solution}")
                    st.write("---")
            else:
                st.write("No crawlability issues detected.")
        progress.progress(8 * progress_step)

        status.text("Checking Accessibility...")
        with col1.expander("♿ Accessibility Insights"):
            access_issues = accessibility_insights(url)
            if access_issues:
                for issue_code, issue_description, solution in access_issues:
                    st.write(f"**Issue ({issue_code}):** {issue_description}")
                    st.write(f"**Solution:** {solution}")
                    st.write("---")
            else:
                st.write("No accessibility issues detected.")
        progress.progress(1.0)  # Mark as 100%

    status.text("Analysis Complete!")


st.markdown("----")

# Add the "Made by Jonathan Boshoff" in the sidebar with a link
st.sidebar.markdown(
    "#### [Made by Jonathan Boshoff](https://jonathanboshoff.com/one-page-seo-audit/)"
)
