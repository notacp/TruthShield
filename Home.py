import streamlit as st
from datetime import datetime
import utils # Assuming utils.py is in the same directory

st.set_page_config(
    page_title="Fact Check Home",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Recent Fact Checks")

# --- State Initialization ---
# Initialize session state variables if they don't exist
if 'home_language' not in st.session_state:
    st.session_state.home_language = 'en' # Default language
if 'home_page_token' not in st.session_state:
    st.session_state.home_page_token = None # Start with no page token (first page)
if 'home_page_history' not in st.session_state:
    st.session_state.home_page_history = [None] # Store history of page tokens, starting with None for the first page

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Language Selection
# Define language options (expand as needed)
language_options = {
    'en': 'English',
    'hi': 'Hindi',
    # Add more languages supported by the API if desired
}
selected_lang_code = st.sidebar.selectbox(
    "Select Language:",
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

# --- API Call --- (Uses session state for language and page token)
# Using query="India" as a potential filter based on PRD suggestion - can be made dynamic later
api_response = utils.call_fact_check_api(
    query="India",
    language_code=st.session_state.home_language,
    page_size=10,
    page_token=st.session_state.home_page_token
)

# --- Display Logic ---
if isinstance(api_response, dict) and "error" in api_response:
    st.error(f"Error: {api_response['error']}")
    if api_response["error"] == "API Key missing":
         st.info("Please ensure your `GOOGLE_API_KEY` is configured in `.streamlit/secrets.toml`")
    st.stop()
elif api_response is None: # Should not happen with new error handling, but good practice
    st.error("Failed to fetch claims from the API. Unknown error.")
    st.stop()

claims = api_response.get('claims', [])
next_page_token = api_response.get('nextPageToken') # Get the token for the *next* page

if not claims and st.session_state.home_page_token is None: # Only show warning if it's the first page and no claims
    st.warning(f"No recent fact checks found for the current filters (Language: {language_options[st.session_state.home_language]}, Query: India).")
else:
    if claims:
        st.write(f"Displaying fact checks (Language: {language_options[st.session_state.home_language]}):")
        for claim in claims:
            utils.display_claim(claim) # Use the display function from utils
    else:
        # This case handles arriving on an empty page via pagination
        st.info("No more fact checks found for the current filters.")

    # --- Pagination Buttons ---
    col1, col2 = st.columns(2)

    with col1:
        # Disable "Previous" if we are on the first page (history has 1 or 0 items)
        if len(st.session_state.home_page_history) > 1:
            if st.button("⬅️ Previous Page"):
                # Remove the current page token from history
                st.session_state.home_page_history.pop()
                # Get the previous page token
                st.session_state.home_page_token = st.session_state.home_page_history[-1]
                st.rerun()
        else:
            st.button("⬅️ Previous Page", disabled=True)

    with col2:
        # Disable "Next" if there is no next page token
        if next_page_token:
            if st.button("Next Page ➡️"):
                # Add the next page token to history and set it as current
                st.session_state.home_page_history.append(next_page_token)
                st.session_state.home_page_token = next_page_token
                st.rerun()
        else:
            st.button("Next Page ➡️", disabled=True) 