import streamlit as st
import utils # Import the utility functions
import google.generativeai as genai
from groq import Groq
import json # To potentially format fact-check results for the LLM

st.set_page_config(page_title="Chat with Fact Checker", page_icon="💬")
st.title("💬 Chat Fact Checker")

# --- Helper Functions ---

def extract_claim_topic(user_query):
    """
    Uses an LLM to extract the core factual claim or topic from the user's query.
    Returns the extracted claim/topic or "NO_CLAIM" if none is found.
    """
    groq_api_key = st.secrets.get("GROQ_API_KEY")
    gemini_api_key = st.secrets.get("GEMINI_API_KEY")

    # Simple prompt for claim extraction
    extraction_prompt = f"""Analyze the following user query: '{user_query}'

Instructions:
Your task is to identify the core factual claim or topic from the user query.
Return ONLY the concise claim/topic string itself.
If the query is a greeting, general chat, a vague request (like "latest news"), or doesn't contain a checkable factual claim, return the exact string "NO_CLAIM".

DO NOT include any explanatory text, labels, or phrases like "Extracted Topic:", "The claim is:", or "The core factual claim or topic being asked about is:".
Your response must be ONLY the extracted claim/topic or the string "NO_CLAIM".

Examples:
- User query: "Is the earth flat?"
  YOUR RESPONSE: "Is the earth flat?"
- User query: "Tell me about the moon landing."
  YOUR RESPONSE: "moon landing"
- User query: "Hi there!"
  YOUR RESPONSE: "NO_CLAIM"
- User query: "What's the news?"
  YOUR RESPONSE: "NO_CLAIM"

User query: '{user_query}'
YOUR RESPONSE:"""

    try:
        if groq_api_key:
            client = Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model="llama-3.1-8b-instant", # Using a smaller model for efficiency
                temperature=0.1,
            )
            extracted_text = completion.choices[0].message.content.strip()
            return extracted_text
        elif gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(extraction_prompt)
            extracted_text = response.text.strip()
            return extracted_text
        else:
            return "NO_CLAIM" # Default to no claim if no API key
    except Exception as e:
        st.error(f"Claim Extraction Error: {e}")
        return "NO_CLAIM" # Return no claim on error

def format_fact_check_results(claims):
    """Formats claim results into a string for the LLM prompt."""
    if not claims:
        return "No fact-check results found for the query."

    formatted_string = "Here are the fact-check results found:\n\n"
    for i, claim in enumerate(claims):
        claim_text = claim.get('text', 'N/A')
        claimant = claim.get('claimant', 'N/A')
        review = claim.get('claimReview', [{}])[0]
        publisher = review.get('publisher', {}).get('name', 'N/A')
        rating = review.get('textualRating', 'N/A')
        review_url = review.get('url', 'N/A')

        formatted_string += f"{i+1}. Claim: {claim_text}\n"
        formatted_string += f"   Claimant: {claimant}\n"
        formatted_string += f"   Rating: {rating} (by {publisher})\n"
        formatted_string += f"   Review URL: {review_url}\n\n"
    return formatted_string.strip()


def get_llm_response(user_query, fact_check_results_str, chat_history):
    """Gets response from the configured LLM (Groq or Gemini)."""
    groq_api_key = st.secrets.get("GROQ_API_KEY")
    gemini_api_key = st.secrets.get("GEMINI_API_KEY")

    system_prompt = (f"You are a helpful and friendly assistant designed to discuss fact-checking information. "
                     f"The user has asked: '{user_query}'.\n\n"
                     f"Here are the fact-check results relevant to their query:\n{fact_check_results_str}\n\n"
                     f"Instructions:\n"
                     f"1. If fact-check results ARE provided, answer the user's query based *only* on those results. Be conversational, mention the key findings (claim, rating, publisher), and include the source URL if available. Do not add information not present in the results.\n"
                     f"2. If the results indicate 'No fact-check results found' or similar, acknowledge this clearly and politely. Ask the user if they can provide a more specific claim or topic they'd like to check.\n"
                     f"3. If the user's input seems like a greeting or general chat unrelated to fact-checking (like 'Hi' or 'How are you?'), respond conversationally without mentioning fact-checking unless they bring it up.\n"
                     f"4. Always be helpful and conversational.")

    # Prepare message history for the LLM
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    # Add previous turns from history
    for turn in chat_history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    # Add the current user query
    messages.append({"role": "user", "content": user_query})


    try:
        if groq_api_key:
            # Use Groq
            client = Groq(api_key=groq_api_key)
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile", # Or another suitable model
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content

        elif gemini_api_key:
            # Use Gemini
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash') # Or another suitable model
            # Gemini uses a different format for history
            gemini_history = []
            current_role = 'user'
            for msg in messages:
                # Combine system prompt with the first user message for Gemini
                if msg["role"] == "system":
                    continue # Skip system message directly
                # Ensure alternating roles for Gemini history
                if msg["role"] == current_role:
                     # If consecutive messages have the same role, append content
                     if gemini_history:
                         gemini_history[-1]['parts'][0] += "\n" + msg["content"]
                     else: # First message (should be user)
                         gemini_history.append({'role': msg["role"], 'parts': [msg["content"]]})
                         current_role = 'model' if msg["role"] == 'user' else 'user'
                else:
                    gemini_history.append({'role': msg["role"], 'parts': [msg["content"]]})
                    current_role = 'model' if msg["role"] == 'user' else 'user'

            # The actual query is the last user message, which might have been merged above
            # Let's adjust to send history and the final query separately if needed by API structure
            # For simplicity here, we send the constructed history directly
            # The system prompt is implicitly handled by the first message content or context setting
            response = model.generate_content(gemini_history)
            # Clean up potential Gemini Markdown response artifacts if necessary
            return response.text.strip()

        else:
            return "Error: No LLM API key found. Please configure GROQ_API_KEY or GEMINI_API_KEY in secrets."

    except Exception as e:
        st.error(f"LLM API Error: {e}")
        return "Sorry, I encountered an error trying to process your request with the language model."


# --- Chat Initialization ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [] # Stores message history {role: "user/assistant", content: "..."}

# Display prior chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Processing ---
if prompt := st.chat_input("Ask about a news claim or topic..."):
    # Add user message to chat history and display it
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process user input
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. Extract claim/topic from user prompt
            extracted_topic = extract_claim_topic(prompt)

            fact_check_results_str = "Please provide a specific claim or topic to check."
            claims = []
            error_message = None

            # 2. Query Fact Check API only if a specific topic was extracted
            if extracted_topic != "NO_CLAIM":
                # Use language from Home page state if available, else default 'en'
                lang_code = st.session_state.get('home_language', 'en')
                fact_check_response = utils.call_fact_check_api(query=extracted_topic, language_code=lang_code, page_size=5)

                # Check for explicit API or Key errors returned by our util function
                if isinstance(fact_check_response, dict) and "error" in fact_check_response:
                    error_message = f"Error fetching fact-check data for '{extracted_topic}': {fact_check_response['error']}"
                    st.warning(error_message)
                    fact_check_results_str = f"Could not retrieve fact-check results for '{extracted_topic}' due to an error: {fact_check_response['error']}"
                # Check if the response is a dict and contains a NON-EMPTY 'claims' list
                elif isinstance(fact_check_response, dict) and 'claims' in fact_check_response and fact_check_response['claims']:
                    claims = fact_check_response['claims']
                    fact_check_results_str = format_fact_check_results(claims)
                # Handle cases where the API call succeeded but found no claims
                # This includes responses like {'claims': []} or just {}
                elif isinstance(fact_check_response, dict):
                    # API call succeeded but found no matching claims for the extracted topic
                    fact_check_results_str = f"No specific fact-check results found for: '{extracted_topic}'."
                # Handle completely unexpected response types (not a dict)
                else:
                    error_message = f"Received an unexpected response type from the fact-check API for '{extracted_topic}': {type(fact_check_response)}"
                    st.warning(error_message)
                    fact_check_results_str = f"Could not retrieve fact-check results for '{extracted_topic}' due to an unexpected API response type."
            # else: If extracted_topic is "NO_CLAIM", we skip the API call and use the default fact_check_results_str

            # 3. Call LLM with fact check results (or explanation) and history
            llm_response = get_llm_response(prompt, fact_check_results_str, st.session_state.chat_messages[:-1])

            # Display LLM response
            st.markdown(llm_response)

            # Add LLM response to chat history
            st.session_state.chat_messages.append({"role": "assistant", "content": llm_response}) 