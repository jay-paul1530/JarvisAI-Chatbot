import os

import streamlit as st
from chatformers.chatbot import chat
import random
import string
from dotenv import load_dotenv

load_dotenv('.env')


LLM_API_KEY = os.getenv('LLM_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')


# Streamlit app settings
st.set_page_config(page_title="Chatbot with LLM", layout="wide")

# Define the model and settings
embedding_model_settings = {
    "provider": 'ollama',
    "base_url": 'http://localhost:11434',
    "model": "nomic-embed-text",
    "api_key": None
}

llm_provider_settings = {
    "provider": 'groq',
    "base_url": 'https://api.groq.com/openai/v1',
    "model": MODEL_NAME,
    "api_key": LLM_API_KEY,
}

chroma_settings = {
    "host": None,
    "port": None,
    "settings": None
}

memory_settings = {
    "try_queries": True,
    "results_per_query": 1,
}

collection_name = "conversation"

# Initialize session state for chat history, unique session id, and unique message id
if "buffer_window_chats" not in st.session_state:
    st.session_state["buffer_window_chats"] = []

# Generate a random unique message ID for the session (persisted until refresh)
if "unique_message_id" not in st.session_state:
    st.session_state["unique_message_id"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# Define personas and their corresponding system prompts
personas = {
    "Default Persona": """You are a helpful assistant. 
Output Format-
- Return all extracted facts as a JSON object with a single key "output", containing a list of strings.
{
'output': <string goes here>
}    
""",
    "Hashtag Generator": """You are a hashtag generator AI agent. Your job is to generate hashtags based on give user 
text / situation / example etc.

Output Format-
- Return the generated hashtags as a comma separated list of strings.
- Do not generate anything else.

Output Examples-
- Example 1:
#Technology, #ArtificialIntelligence, #Economics
- Example 2:
#Startup, #Marketing, #Design
- Example 3:
#Business, #Marketing, #Finance

""",
    "Tech Guru": "You are an expert in technology, able to explain complex technical topics in simple terms.",
    "Friendly Companion": "You are a cheerful and friendly assistant, always ready to offer positive support.",
    "Professional Advisor": "You are a professional advisor, providing logical and business-oriented insights.",
    "Creative Thinker": "You are a creative assistant who thinks outside the box and suggests innovative ideas."
}

# Sidebar for chat settings
st.sidebar.title("Chat Settings")

# Ask user for a unique username to be used as session id
unique_username = st.sidebar.text_input("Enter your unique username:", "")

# Dropdown for persona selection
selected_persona = st.sidebar.selectbox("Select Persona:", list(personas.keys()))

# System prompt based on selected persona
system_message = personas[selected_persona]

# Display selected persona in the sidebar
st.sidebar.write(f"Current Persona: **{selected_persona}**")

if unique_username:
    unique_session_id = f"{unique_username}{selected_persona.replace(' ', '')}"  # Use the unique username as the session ID
else:
    st.sidebar.warning("Please enter a unique username to start the chat.")
    st.stop()

# Title and description
st.title("LLM-Powered Chatbot")
st.write(f"Chatting as: **{unique_username}**")

# Input box for user query
query = st.text_input("Your message:", "")

# Submit button to send the query
if st.button("Send") and query:
    # Call the backend chat function with the user's query and the selected persona's system message
    response = chat(
        query=query,
        system_message=system_message + " Generate replies in 100 to 300 words max.",  # Use the selected persona's system prompt
        llm_provider_settings=llm_provider_settings,
        chroma_settings=chroma_settings,
        embedding_model_settings=embedding_model_settings,
        memory_settings=memory_settings,
        memory=True,
        summarize_memory=False,
        collection_name=collection_name,
        unique_session_id=unique_session_id,  # Dynamic session ID from user input
        unique_message_id=st.session_state["unique_message_id"],  # Randomly generated message ID
        buffer_window_chats=st.session_state["buffer_window_chats"],
    )

    # Append the user query and response to the chat history
    st.session_state["buffer_window_chats"].append({'role': 'user', 'content': query})
    st.session_state["buffer_window_chats"].append({'role': 'assistant', 'content': response})

# Display the conversation history
if st.session_state["buffer_window_chats"]:
    st.subheader("Conversation History")
    for chat_item in st.session_state["buffer_window_chats"]:
        role = "User" if chat_item['role'] == 'user' else "Assistant"
        st.markdown(f"**{role}:** {chat_item['content']}")
