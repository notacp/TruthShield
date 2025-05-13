import streamlit as st
import requests
import os
from datetime import datetime # Added for display_claim
import json # Import json for JSONDecodeError
import re # Import re for regex-based HTML parsing
from bs4 import BeautifulSoup

# Ensure GOOGLE_API_KEY is set as an environment variable or in Streamlit secrets
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
API_ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

@st.cache_data(ttl=3600) # Cache API calls for 1 hour
def call_fact_check_api(query: str = None, language_code: str = 'en', page_size: int = 10, page_token: str = None):
    """
    Calls the Google Fact Check Tools API (Cached).

    Args:
        query (str, optional): The query string. Defaults to None.
        language_code (str, optional): Language code (e.g., 'en'). Defaults to 'en'.
        page_size (int, optional): Number of results per page. Defaults to 10.
        page_token (str, optional): Token for the next page of results. Defaults to None.

    Returns:
        dict: The JSON response from the API, or a dict with an 'error' key if an error occurs.
              Should never return None.
    """
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "API Key missing"}

    params = {
        'key': api_key,
        'languageCode': language_code,
        'pageSize': page_size,
    }
    if query:
        params['query'] = query
    if page_token:
        params['pageToken'] = page_token

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

        if not response.content:
            return {'claims': []}

        return response.json()

    except requests.exceptions.HTTPError as e:
        error_detail = f"HTTP Error: {e.response.status_code} {e.response.reason}"
        try:
            error_body = e.response.json()
            error_detail += f" - {error_body}"
        except json.JSONDecodeError:
            error_detail += f" - {e.response.text}"
        return {"error": error_detail}

    except requests.exceptions.RequestException as e:
        return {"error": f"API Request Error: {e}"}

    except json.JSONDecodeError as e:
        return {"error": f"API JSON Decode Error: {e}. Response text: {response.text[:500]}..."}

    except Exception as e:
        return {"error": f"An unexpected error occurred in API call: {type(e).__name__} - {e}"}

def scrape_images_from_url(url, max_images=5, timeout=10):
    """
    Fetches up to `max_images` image URLs from the given webpage URL.
    Tries Open Graph, Twitter Card, and <img> tags as fallbacks.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    images = []

    # Try Open Graph
    og = soup.find('meta', property='og:image')
    if og and og.get('content'):
        images.append(og['content'])

    # Try Twitter Card
    tc = soup.find('meta', attrs={'name': 'twitter:image'})
    if tc and tc.get('content'):
        images.append(tc['content'])

    # Fallback to <link rel="image_src">
    link_img = soup.find('link', rel='image_src')
    if link_img and link_img.get('href'):
        images.append(link_img['href'])

    # Fallback to regular <img>
    for img in soup.find_all('img', src=True):
        src = img['src']
        if src not in images:
            images.append(src)
        if len(images) >= max_images:
            break

    return images[:max_images]

# Helper to get image
def get_thumbnail_for_review(review_url):
    if review_url:
        # scrape_images_from_url is defined above
        image_urls = scrape_images_from_url(review_url, max_images=1) 
        if image_urls:
            return image_urls[0]
    return None

# Function to render a single gallery card
def render_gallery_card(claim_data, claim_key): # claim_key is important for unique widget keys
    claim_text = claim_data.get('text', 'N/A')
    claim_reviews = claim_data.get('claimReview', [])
    
    review_url = None
    textual_rating = "N/A" # Default status
    publisher_name_for_alt = "Review"

    if claim_reviews:
        review = claim_reviews[0]
        review_url = review.get('url')
        textual_rating = review.get('textualRating', 'N/A')
        publisher_name_for_alt = review.get('publisher', {}).get('name', 'Review')

    thumbnail_url = get_thumbnail_for_review(review_url)

    with st.container(border=True): # Simple card look
        # Image container for relative positioning of the badge
        st.markdown("<div style='position: relative; width: 100%;'>", unsafe_allow_html=True)
        
        if thumbnail_url:
            # Image fills the container width, maintain aspect ratio via CSS if needed by browser
            st.image(thumbnail_url, use_container_width=True, caption="") # caption set to empty or remove if not needed
        else:
            # Placeholder that respects column width and has a decent aspect ratio
            st.markdown("""
                <div style='
                    width:100%; 
                    aspect-ratio: 16/9; 
                    background-color:#f0f0f0; 
                    display:flex; 
                    flex-direction:column; 
                    align-items:center; 
                    justify-content:center; 
                    border-radius: 4px;
                '>
                🖼️<br/>No Image
                </div>
            """, unsafe_allow_html=True)
        
        # Status Badge
        # Basic styling for the badge - can be enhanced
        badge_color = {
            "true": "#28a745", # Green for True
            "false": "#dc3545", # Red for False
            "misleading": "#ffc107", # Yellow for Misleading
            "partially true": "#17a2b8", # Teal for Partially True
            "other": "#6c757d" # Grey for others
        }.get(textual_rating.lower(), "#6c757d") # Default to grey

        st.markdown(f"""
            <div style='
                position: absolute; 
                top: 4px; 
                right: 4px; 
                background-color: {badge_color};
                color: white; 
                padding: 2px 8px; 
                border-radius: 4px; 
                font-size: 0.75em; 
                font-weight: bold;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100px;
            '>
            {textual_rating}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True) # Close the relative_image_container
        
        # Title - always visible, allows wrapping
        # Adjust min-height as needed, or remove if dynamic height is fully okay
        st.markdown(f"""
            <p style='
                font-size: 0.9em; 
                font-weight: bold; 
                margin-top: 8px; 
                min-height: 2.5em; /* Ensure space, but allow expansion */
                line-height: 1.2em;
                text-align: center;
                word-wrap: break-word; /* Ensure long words don't overflow */
            '>
            {claim_text}
            </p>
        """, unsafe_allow_html=True)

        # Define view details function to set loading state
        def view_details():
            # Simply update the selected claim key
            st.session_state.selected_claim_key = claim_key

        if st.button("View Details", key=f"details_{claim_key}", use_container_width=True, on_click=view_details):
            # The on_click callback will handle setting the state
            pass

# Function to render the detailed view of a claim (e.g., in a dialog)
def render_claim_details(claim_data):
    claim_text = claim_data.get('text', 'N/A')
    claim_reviews = claim_data.get('claimReview', [])

    review_url_for_thumb = None
    publisher_name_for_alt = "Review"
    if claim_reviews:
        review = claim_reviews[0] # Get the first review
        review_url_for_thumb = review.get('url')
        publisher_name_for_alt = review.get('publisher', {}).get('name', 'Review')

    thumbnail_url = get_thumbnail_for_review(review_url_for_thumb)

    # Layout for details: image on left (optional), text on right, or image above text
    # For a dialog, often image above or a more compact layout is good.
    
    if thumbnail_url:
        st.image(thumbnail_url, caption=publisher_name_for_alt, use_container_width=True) # Or a fixed width: width=200
    else:
        # Smaller placeholder for details view
        st.markdown("<div style='width:100%; height:150px; background-color:#f0f0f0; display:flex; flex-direction:column; align-items:center; justify-content:center; border-radius: 4px;'>🖼️<br/>No Image</div>", unsafe_allow_html=True)

    st.subheader(claim_text) # Display the full claim text as subheader

    if claim_reviews:
        # Details from the first claimReview
        review = claim_reviews[0]
        publisher = review.get('publisher', {})
        publisher_name = publisher.get('name', 'N/A')
        publisher_site = publisher.get('site', 'N/A')
        review_date_str = review.get('reviewDate')
        rating = review.get('textualRating', 'N/A')
        review_url = review.get('url') # This is the URL to the fact-check article

        # Date formatting helper function (defined locally)
        def get_day_with_suffix(day):
            if 11 <= day <= 13: return str(day) + 'th'
            suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
            return str(day) + suffixes.get(day % 10, 'th')

        review_date_formatted = "N/A"
        review_time_formatted = ""
        if review_date_str:
            try:
                # Ensure datetime is imported: from datetime import datetime
                dt_obj = datetime.fromisoformat(review_date_str.replace('Z', '+00:00'))
                day_with_suffix = get_day_with_suffix(dt_obj.day)
                review_date_formatted = dt_obj.strftime(f"%A, {day_with_suffix} %B %Y")
                review_time_formatted = dt_obj.strftime("%I:%M%p").lower()
            except ValueError:
                # Fallback if date parsing fails
                review_date_formatted = review_date_str 
        
        st.markdown(f"**Rating:** {rating}")
        st.markdown(f"**Reviewed by:** {publisher_name} ({publisher_site or 'N/A'})")
        if review_time_formatted:
            st.markdown(f"**Review Date:** {review_date_formatted} at {review_time_formatted}")
        else:
            st.markdown(f"**Review Date:** {review_date_formatted}")

        if review_url:
            st.link_button("Read Full Review", review_url, use_container_width=True)
        else:
            st.markdown("Review URL: N/A")
    else:
        st.markdown("No review details available for this claim.")

# Example Usage (can be commented out or removed)
# if __name__ == '__main__':
#     # Requires running with streamlit run utils.py and secrets configured
#     if 'GOOGLE_API_KEY' in st.secrets:
#         # Example: Fetch first page
#         results = call_fact_check_api(query="India", language_code='en', page_size=5)
#         if results and not results.get("error"):
#             st.write("### Page 1 Results:")
#             st.write(results)
#             next_page_token = results.get('nextPageToken')
#             if next_page_token:
#                 st.success(f"Next page token found: {next_page_token}")
#                 # Example: Fetch second page if token exists
#                 results_page_2 = call_fact_check_api(query="India", language_code='en', page_size=5, page_token=next_page_token)
#                 if results_page_2 and not results_page_2.get("error"):
#                      st.write("### Page 2 Results:")
#                      st.write(results_page_2)
#                 elif results_page_2 and results_page_2.get("error"):
#                      st.error(f"Error fetching page 2: {results_page_2['error']}")
#                 else:
#                     st.warning("Failed to fetch page 2.")

#         elif results and results.get("error"):
#             st.error(f"API Error: {results['error']}")
#         else:
#             st.write("Failed to fetch results.")
#     else:
#         st.error("Please provide GOOGLE_API_KEY in .streamlit/secrets.toml")