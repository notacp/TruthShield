# TruthShield: Fact Checking Application

A Streamlit application that allows users to search for and view fact checks from the Google Fact Check Tools API, as well as chat with an AI assistant about fact checking topics.

## Features

- Browse recent fact checks with pagination
- Search for specific fact checks
- View detailed information about each fact check
- Chat with an AI assistant to discuss and verify claims
- Multi-language support (English, Hindi)

## Setup

### Prerequisites

- Python 3.8+
- Streamlit
- A Google API key for the Fact Check Tools API
- An LLM API key (Groq or Gemini) for the chat feature

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/truthshield.git
   cd truthshield
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   
   Create or modify the `.streamlit/secrets.toml` file:
   ```toml
   # .streamlit/secrets.toml
   GOOGLE_API_KEY = "your_google_api_key"
   
   # Add ONE of these LLM API keys
   GROQ_API_KEY = "your_groq_api_key"
   # GEMINI_API_KEY = "your_gemini_api_key" 
   ```

## Running Locally

Run the application locally with:

```
streamlit run Home.py
```

The application should open in your default web browser at `http://localhost:8501`.

## Deployment

### Deploy to Streamlit Cloud

1. Push your code to a GitHub repository

2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)

3. Create a new app:
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to `Home.py`
   - Add your secrets in the Streamlit Cloud dashboard (under "Advanced settings" > "Secrets")

4. Deploy your app

### Deploy to Other Platforms

The application can also be deployed to platforms like Heroku, AWS, GCP, or Azure:

- Use the provided `requirements.txt` 
- Set environment variables for your API keys
- Set the command to run the application: `streamlit run Home.py`

## Project Structure

- `Home.py`: Main application page with fact check listing and search
- `pages/Chat.py`: Chat interface for discussing fact checks
- `utils.py`: Utility functions for API calls and UI components
- `.streamlit/`: Configuration directory for Streamlit
- `requirements.txt`: Application dependencies

## License

[MIT License](LICENSE) 