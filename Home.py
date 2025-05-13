import streamlit as st
from datetime import datetime
import utils # Assuming utils.py is in the same directory

# --- Streamlit Configuration ---
st.set_page_config(
    page_title="TruthShield - Fact Check Home",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://github.com/yourusername/truthshield',
        'Report a bug': 'https://github.com/yourusername/truthshield/issues',
        'About': "# TruthShield\nA fact-checking application powered by Google Fact Check Tools API."
    }
)

# Add Flaticon UIcon stylesheet
st.markdown("""
<link rel='stylesheet' href='https://cdn-uicons.flaticon.com/uicons-regular-straight/css/uicons-regular-straight.css'>
""", unsafe_allow_html=True)

# --- State Initialization ---
# Initialize session state variables if they don't exist
if 'home_language' not in st.session_state:
    st.session_state.home_language = 'en' # Default language
if 'home_page_token' not in st.session_state:
    st.session_state.home_page_token = None # Start with no page token (first page)
if 'home_page_history' not in st.session_state:
    st.session_state.home_page_history = [None] # Store history of page tokens, starting with None for the first page
if 'selected_claim_key' not in st.session_state: # For storing the key (index) of the selected claim for detail view
    st.session_state.selected_claim_key = None
if 'loading' not in st.session_state: # Track loading state
    st.session_state.loading = False
if 'search_query' not in st.session_state: # Store the current search query
    st.session_state.search_query = ""
if 'search_results' not in st.session_state: # Store search results
    st.session_state.search_results = None
if 'api_error' not in st.session_state: # Track API errors
    st.session_state.api_error = None

# Reset loading state at the beginning of each run
if st.session_state.loading:
    st.session_state.loading = False

# --- Title Row with Language Selection on Right ---
col_title, col_lang = st.columns([4, 1])

with col_title:
    st.markdown("<h1><i class='fi fi-rs-house-chimney'></i> TruthShield: Recent Fact Checks</h1>", unsafe_allow_html=True)

with col_lang:
    # Language Selection
    # Define language options (expand as needed)
    language_options = {
        'en': 'English',
        'hi': 'Hindi',
        # Add more languages supported by the API if desired
    }
    selected_lang_code = st.selectbox(
        "Language:",
        options=list(language_options.keys()),
        format_func=lambda code: language_options[code],
        key='home_language_selector' # Use a separate key for the widget itself
    )

    # Update session state if the selection changes
    if selected_lang_code != st.session_state.home_language:
        st.session_state.home_language = selected_lang_code
        # Reset pagination when language changes
        st.session_state.home_page_token = None
        st.session_state.home_page_history = [None]
        st.rerun() # Rerun to fetch data with the new language

# --- CSS for Custom Loader and Button Alignment ---
st.markdown("""
<style>
.loader {
  border: 6px solid #f3f3f3;
  border-radius: 50%;
  border-top: 6px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Custom styling for button to match input height */
.stButton > button {
  height: 38px !important;  /* Match Streamlit's default input height */
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}


/* Icon styling */
i.fi {
  margin-right: 0px;
}

/* Vertically center form submit buttons */
div[data-testid="stForm"] .stButton > button {
  margin-top: 5px !important;
}
</style>
""", unsafe_allow_html=True)

# Clear search and return to browsing
def clear_search():
    st.session_state.search_query = ""
    st.session_state.search_results = None
    if 'search_error' in st.session_state:
        del st.session_state.search_error

# --- Search Bar ---
# Use a form to better align the elements
with st.form(key="search_form", clear_on_submit=False):
    col_search1, col_search2 = st.columns([4, 1])
    with col_search1:
        search_query = st.text_input("Search for claims:", key="search_input", value=st.session_state.search_query)
    with col_search2:
        # Can't use HTML in form_submit_button, use plain text instead
        search_button = st.form_submit_button("Search")
    
# Handle clear search button separately (outside the form)
if st.session_state.search_results is not None:
    # Use plain text instead of HTML
    if st.button("Clear Search", key="clear_search"):
        clear_search()
        st.rerun()

# Handle search logic
def perform_search():
    with st.spinner("Searching..."):
        # Call the API using the function from utils.py
        api_response = utils.call_fact_check_api(
            query=st.session_state.search_query, 
            language_code=st.session_state.home_language, 
            page_size=20  # Fetch more results for search
        )
        
        # Store results in session state
        if api_response and not api_response.get("error"):
            st.session_state.search_results = api_response.get('claims', [])
        elif api_response and api_response.get("error"):
            st.session_state.search_error = api_response["error"]
        else:
            st.session_state.search_error = "Unknown error during API call."

# Process search form submission
if search_button and search_query.strip():
    st.session_state.search_query = search_query.strip()
    perform_search()
    # Don't need st.rerun() here as the form submission will trigger a rerun
    
# Clear search if the search box is emptied and user submits
if search_button and st.session_state.search_query and not search_query.strip():
    clear_search()
    # Form submission will trigger a rerun

# Show spinner while loading
if st.session_state.loading:
    st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center">Loading content...</p>', unsafe_allow_html=True)

# --- Define navigation callback functions without st.rerun() ---
def go_to_previous_page():
    st.session_state.home_page_history.pop()
    st.session_state.home_page_token = st.session_state.home_page_history[-1]

def go_to_next_page():
    st.session_state.home_page_history.append(next_page_token)
    st.session_state.home_page_token = next_page_token

def view_claim_details(claim_key):
    st.session_state.selected_claim_key = claim_key

def go_back_to_gallery():
    st.session_state.selected_claim_key = None

# --- API Call ---
# Only make regular API call if not showing search results
api_response = None
if st.session_state.search_results is None:
    api_response = utils.call_fact_check_api(
        query="India", # Example query
        language_code=st.session_state.home_language,
        page_size=10, # Or any other suitable page size for gallery
        page_token=st.session_state.home_page_token
    )

    claims = api_response.get('claims', [])
    next_page_token = api_response.get('nextPageToken')

# --- Display Logic ---
if st.session_state.selected_claim_key is not None:
    # --- Detail View ---
    selected_index = None
    try:
        # The key stored by render_gallery_card is the index
        selected_index = int(st.session_state.selected_claim_key)
    except (ValueError, TypeError):
        st.error("Invalid claim selection key. Returning to gallery.")
        st.session_state.selected_claim_key = None
        st.rerun()

    if selected_index is not None and 0 <= selected_index < len(claims):
        selected_claim_data = claims[selected_index]

        # Use plain text instead of HTML
        st.button("Back to Gallery", on_click=go_back_to_gallery, key="back_to_gallery_button")
        utils.render_claim_details(selected_claim_data)
    else:
        # This can happen if claims list changed (e.g. user navigated pages in another tab, or data changed)
        # or if the key was invalid.
        st.warning("Could not display the selected claim. It might not be available on the current page. Returning to gallery.")
        st.session_state.selected_claim_key = None
        st.rerun()

else:
    # Either show search results or regular browsing content
    if st.session_state.search_results is not None:
        # --- Search Results Display ---
        if 'search_error' in st.session_state:
            st.error(f"Error: {st.session_state.search_error}")
        elif not st.session_state.search_results:
            st.warning(f"No fact checks found matching: {st.session_state.search_query}")
        else:
            st.subheader(f"Search Results for: {st.session_state.search_query}")
            st.write(f"Found {len(st.session_state.search_results)} results:")
            
            # Display search results in a gallery format
            num_columns = 3  # Number of columns in the gallery
            cols = st.columns(num_columns)
            for i, claim_data in enumerate(st.session_state.search_results):
                with cols[i % num_columns]:
                    utils.render_gallery_card(claim_data, claim_key=i)
    else:
        # --- Gallery View ---
        # Regular error handling for the normal API response
        if isinstance(api_response, dict) and "error" in api_response:
            st.error(f"Error: {api_response['error']}")
            if api_response["error"] == "API Key missing":
                st.info("Please ensure your `GOOGLE_API_KEY` is configured in `.streamlit/secrets.toml`")
            st.stop()
        elif api_response is None:
            st.error("Failed to fetch claims from the API. Unknown error.")
            st.stop()

        if not claims and st.session_state.home_page_token is None:
            st.warning(f"No recent fact checks found for the current filters (Language: {language_options[st.session_state.home_language]}, Query: India).")
        elif claims:
            st.write(f"Displaying fact checks (Language: {language_options[st.session_state.home_language]}):")
            
            num_columns = 3  # Number of columns in the gallery
            cols = st.columns(num_columns)
            for i, claim_data in enumerate(claims):
                with cols[i % num_columns]:
                    utils.render_gallery_card(claim_data, claim_key=i)
        else:
            st.info("No more fact checks found for the current filters.")

        # --- Pagination Buttons (Only show in Gallery View) ---
        # Use a 3-column layout to position buttons with proper alignment
        left_col, spacer_col, right_col = st.columns([1, 3, 1])

        with left_col:
            if len(st.session_state.home_page_history) > 1:
                # Use standard button with text arrow
                if st.button("← Previous Page", key="prev_page_btn", on_click=go_to_previous_page):
                    pass
            else:
                st.button("← Previous Page", key="prev_page_disabled", disabled=True)

        # Right-align the Next Page button 
        with right_col:
            if next_page_token:
                # Use standard button with text arrow
                if st.button("Next Page →", key="next_page_btn", on_click=go_to_next_page):
                    pass
            else:
                st.button("Next Page →", key="next_page_disabled", disabled=True)