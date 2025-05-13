import streamlit as st
import utils # Import the utility functions

st.set_page_config(page_title="Search Claims", page_icon="🔍")
st.title("🔍 Search Fact Checks")

# --- Search Input ---
search_query = st.text_input("Enter a claim or topic to search:", key="search_query_input")
search_button = st.button("Search", key="search_button")

# --- Search Execution and Display ---
if search_button or (search_query and 'search_results' in st.session_state): # Persist results if already searched
    if not search_query:
        st.toast("⚠️ Please enter a search query.")
    else:
        # Use session state to store results only if triggering a new search
        if search_button:
            # Clear previous results before new search
            if 'search_results' in st.session_state:
                del st.session_state['search_results']
                del st.session_state['search_query']

            with st.spinner("Searching..."):
                # Call the API using the function from utils.py
                # Use default language 'en', can be enhanced with language selector later
                api_response = utils.call_fact_check_api(query=search_query, language_code='en', page_size=20) # Fetch more results for search

                # Store results and query in session state upon successful fetch
                if api_response and not api_response.get("error"):
                    st.session_state.search_results = api_response.get('claims', [])
                    st.session_state.search_query = search_query # Store the query that yielded these results
                elif api_response and api_response.get("error"):
                     st.session_state.search_error = api_response["error"]
                else:
                    st.session_state.search_error = "Unknown error during API call."

        # --- Display Results (from session state if available) ---
        if 'search_error' in st.session_state:
            st.error(f"Error: {st.session_state.search_error}")
            # Optionally clear the error after displaying
            # del st.session_state.search_error

        elif 'search_results' in st.session_state:
            results = st.session_state.search_results
            if results:
                st.subheader(f"Search Results for: " + st.session_state.search_query)
                st.write(f"Found {len(results)} results:")
                for claim in results:
                    utils.display_claim(claim)
                # Basic pagination placeholder for search (can be implemented similar to home)
                # next_page_token = api_response.get('nextPageToken') if 'api_response' in locals() else None
                # if next_page_token:
                #     st.write("More results might be available...")
            else:
                st.warning(f"No fact checks found matching: " + st.session_state.search_query)
        elif not search_button: # Avoid showing spinner if just displaying persisted results
             pass # If search_results is not in session state and button not clicked, do nothing


# Instructions or placeholder text when the page loads initially or input is cleared
if not search_query and 'search_results' not in st.session_state and 'search_error' not in st.session_state:
    st.info("Enter a topic (e.g., 'COVID-19 vaccine safety') or a specific claim to search for fact checks.") 