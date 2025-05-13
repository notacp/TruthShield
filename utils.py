import streamlit as st
import requests
import os
from datetime import datetime # Added for display_claim
import json # Import json for JSONDecodeError
import re # Import re for regex-based HTML parsing

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

def display_claim(claim):
    """Displays a single claim in a formatted card with a thumbnail."""
    with st.container(border=True):
        col1, col2 = st.columns([1, 4])  # Thumbnail column, Text details column

        claim_text = claim.get('text', 'N/A')
        claim_reviews = claim.get('claimReview', [])

        if claim_reviews:
            review = claim_reviews[0]
            publisher = review.get('publisher', {})
            publisher_name = publisher.get('name', 'N/A')
            publisher_site = publisher.get('site', 'N/A')
            review_date_str = review.get('reviewDate')
            rating = review.get('textualRating', 'N/A')
            review_url = review.get('url')

            thumbnail_url = None
            image_info = review.get('image')
            if isinstance(image_info, dict):
                thumbnail_url = image_info.get('url')
            elif isinstance(image_info, list) and len(image_info) > 0 and isinstance(image_info[0], dict):
                thumbnail_url = image_info[0].get('url')

            if not thumbnail_url:
                review_rating_info = review.get('reviewRating', {})
                if isinstance(review_rating_info, dict):
                    thumbnail_url = review_rating_info.get('imageUrl')
                    if not thumbnail_url:
                        rating_image_obj = review_rating_info.get('image')
                        if isinstance(rating_image_obj, dict):
                            thumbnail_url = rating_image_obj.get('url')

            if not thumbnail_url:
                publisher_info = review.get('publisher', {})
                if isinstance(publisher_info, dict):
                    publisher_image_obj = publisher_info.get('image')
                    if isinstance(publisher_image_obj, dict):
                        thumbnail_url = publisher_image_obj.get('url')
                    elif isinstance(publisher_image_obj, list) and len(publisher_image_obj) > 0 and isinstance(publisher_image_obj[0], dict):
                        thumbnail_url = publisher_image_obj[0].get('url')
            
            # NEW: If no thumbnail_url found yet, try to scrape it from review_url
            if not thumbnail_url and review_url:
                try:
                    page_response = requests.get(review_url, timeout=10) # Increased timeout
                    page_response.raise_for_status()
                    html_content = page_response.text

                    # Try to find Open Graph image meta tag
                    og_pattern = r'<meta\s+property=["']og:image["']\s+content=["'](.*?)["']\s*/?>'
                    og_image_match = re.search(og_pattern, html_content, re.IGNORECASE)
                    if og_image_match:
                        thumbnail_url = og_image_match.group(1)
                    else:
                        # Fallback: Try to find Twitter card image meta tag
                        twitter_pattern = r'<meta\s+name=["']twitter:image["']\s+content=["'](.*?)["']\s*/?>'
                        twitter_image_match = re.search(twitter_pattern, html_content, re.IGNORECASE)
                        if twitter_image_match:
                            thumbnail_url = twitter_image_match.group(1)

                except requests.exceptions.RequestException as e:
                    # Using simple strings for warnings to avoid f-string parsing issues with linter
                    warning_message = "Could not fetch review URL (" + review_url + ") for thumbnail: " + str(e)
                    st.warning(warning_message)
                except Exception as e: 
                    warning_message = "Error processing review URL (" + review_url + ") for thumbnail: " + str(e)
                    st.warning(warning_message)

            with col1:
                if thumbnail_url:
                    st.markdown(
                        f"""
                        <style>
                            .circular-image img {{
                                border-radius: 50%;
                                width: 100px;
                                height: 100px;
                                object-fit: cover;
                            }}
                        </style>
                        <div class="circular-image">
                            <img src="{thumbnail_url}" alt="{publisher_name or 'Review Image'}">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown("<div style='width:100px; height:100px; background-color:#f0f0f0; display:flex; align-items:center; justify-content:center; border-radius:50%;'>🖼️</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"{claim_text}")

                review_date_formatted = "N/A"
                review_time_formatted = ""

                if review_date_str:
                    try:
                        dt_obj = datetime.fromisoformat(review_date_str.replace('Z', '+00:00'))
                        
                        def get_day_with_suffix(day):
                            if 11 <= day <= 13:
                                return str(day) + 'th'
                            suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
                            return str(day) + suffixes.get(day % 10, 'th')

                        day_with_suffix = get_day_with_suffix(dt_obj.day)
                        review_date_formatted = dt_obj.strftime(f"%A, {day_with_suffix} %B %Y")
                        review_time_formatted = dt_obj.strftime("%I:%M%p").lower()
                    except ValueError:
                        review_date_formatted = review_date_str 
                        review_time_formatted = ""

                st.markdown(f"**Rating:** {rating}")
                st.markdown(f"**Reviewed by:** {publisher_name} ({publisher_site})")
                if review_time_formatted:
                    st.markdown(f"**Review Date:** {review_date_formatted} at {review_time_formatted}")
                else:
                    st.markdown(f"**Review Date:** {review_date_formatted}")

                if review_url:
                    st.link_button("Read Review", review_url)
                else:
                    st.markdown("Review URL: N/A")
        else: 
            with col1:
                 st.markdown("<div style='width:100px; height:100px; background-color:#f0f0f0; display:flex; align-items:center; justify-content:center; border-radius:50%;'>🖼️</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"{claim_text}")
                st.markdown("No review details available.")

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