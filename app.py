import streamlit as st
import os
import requests
from pathlib import Path
import json

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_URL = "https://huggingface.co/tfdtfd/khisbagis23/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true"

PRESET_PROMPTS = {
    "Khisba GIS": """You are Khisba GIS, an enthusiastic remote sensing and GIS expert. Your personality:
- Name: Khisba GIS
- Role: Remote sensing and GIS expert
- Style: Warm, friendly, and approachable
- Expertise: Deep knowledge of satellite imagery, vegetation indices, and geospatial analysis
- Humor: Light and professional
- Always eager to explore new remote sensing challenges

Guidelines:
- Focus primarily on remote sensing, GIS, and satellite imagery topics
- Be naturally enthusiastic about helping with vegetation indices and analysis
- Share practical examples and real-world applications
- Show genuine interest in the user's remote sensing challenges
- If topics go outside remote sensing, gently guide back to GIS
- Always introduce yourself as Khisba GIS when asked who you are""",
    "Default Assistant": "You are a helpful, friendly AI assistant. Provide clear and concise answers.",
    "Professional Expert": "You are a professional expert. Provide detailed, accurate, and well-structured responses. Use formal language and cite reasoning when appropriate.",
    "Creative Writer": "You are a creative writer with a vivid imagination. Use descriptive language, metaphors, and engaging storytelling in your responses.",
    "Code Helper": "You are a programming expert. Provide clean, well-commented code examples. Explain technical concepts clearly and suggest best practices.",
    "Friendly Tutor": "You are a patient and encouraging tutor. Explain concepts step by step, use simple examples, and ask questions to ensure understanding.",
    "Concise Responder": "You are brief and to the point. Give short, direct answers without unnecessary elaboration.",
    "Custom": ""
}

# Search APIs
SEARCH_TOOLS = {
    "ArXiv": {
        "name": "ArXiv Scientific Papers",
        "icon": "📚",
        "description": "Search scientific papers",
        "endpoint": "http://export.arxiv.org/api/query"
    },
    "DuckDuckGo": {
        "name": "DuckDuckGo Instant Answers",
        "icon": "🔍",
        "description": "Get instant answers",
        "endpoint": "https://api.duckduckgo.com/"
    },
    "Weather": {
        "name": "Weather",
        "icon": "🌤️",
        "description": "Get weather information",
        "endpoint": "https://wttr.in/"
    },
    "Wikipedia": {
        "name": "Wikipedia",
        "icon": "📖",
        "description": "Search Wikipedia",
        "endpoint": "https://en.wikipedia.org/w/api.php"
    }
}

st.set_page_config(
    page_title="TinyLLaMA Chat",
    page_icon="🦙",
    layout="centered"
)

st.title("🦙 TinyLLaMA Chat")
st.caption("A local AI chat powered by TinyLLaMA 1.1B")

def download_model():
    """Download the model from Hugging Face with progress."""
    MODEL_DIR.mkdir(exist_ok=True)
    
    st.info("📥 Downloading YOUR TinyLLaMA model from Hugging Face...")
    
    try:
        response = requests.get(MODEL_URL, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download model: {str(e)}")
    
    total_size = int(response.headers.get('content-length', 0))
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    downloaded = 0
    try:
        with open(MODEL_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = downloaded / total_size
                        progress_bar.progress(progress)
                        status_text.text(f"Downloading: {downloaded / (1024**2):.1f} / {total_size / (1024**2):.1f} MB")
    except Exception as e:
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        raise Exception(f"Download interrupted: {str(e)}")
    
    if total_size > 0 and downloaded != total_size:
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        raise Exception(f"Incomplete download: got {downloaded} bytes, expected {total_size}")
    
    progress_bar.empty()
    status_text.empty()
    
    # Verify the download
    if MODEL_PATH.exists():
        file_size = MODEL_PATH.stat().st_size / (1024**3)
        st.success(f"✅ Download successful! File size: {file_size:.2f} GB")
        return True
    else:
        raise Exception("❌ Download failed")

@st.cache_resource(show_spinner=False)
def load_model():
    """Load the TinyLLaMA model using ctransformers."""
    from ctransformers import AutoModelForCausalLM
    
    if not MODEL_PATH.exists():
        download_model()
    
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL_DIR),
        model_file=MODEL_PATH.name,
        model_type="llama",
        context_length=2048,
        gpu_layers=0
    )
    return model

def search_arxiv(query, max_results=3):
    """Search ArXiv for scientific papers."""
    try:
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        response = requests.get(SEARCH_TOOLS["ArXiv"]["endpoint"], params=params)
        response.raise_for_status()
        
        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        results = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
            authors = [author.find('{http://www.w3.org/2005/Atom}name').text 
                      for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
            results.append({
                'title': title,
                'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                'authors': ', '.join(authors[:3])
            })
        return results
    except Exception as e:
        return [{"error": f"ArXiv search failed: {str(e)}"}]

def search_duckduckgo(query):
    """Search DuckDuckGo for instant answers."""
    try:
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        response = requests.get(SEARCH_TOOLS["DuckDuckGo"]["endpoint"], params=params)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        if data.get('AbstractText'):
            result['abstract'] = data['AbstractText']
        if data.get('RelatedTopics'):
            related = [topic.get('Text', '') for topic in data['RelatedTopics'][:3]]
            result['related'] = related
        return result
    except Exception as e:
        return {"error": f"DuckDuckGo search failed: {str(e)}"}

def get_weather(location="London"):
    """Get weather information for a location."""
    try:
        response = requests.get(f"{SEARCH_TOOLS['Weather']['endpoint']}/{location}?format=j1")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Weather lookup failed: {str(e)}"}

def search_wikipedia(query):
    """Search Wikipedia for articles."""
    try:
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': 3
        }
        response = requests.get(SEARCH_TOOLS["Wikipedia"]["endpoint"], params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data['query']['search']:
            results.append({
                'title': item['title'],
                'snippet': item['snippet']
            })
        return results
    except Exception as e:
        return [{"error": f"Wikipedia search failed: {str(e)}"}]

def format_prompt(messages, system_prompt=""):
    """Format conversation history for TinyLLaMA chat format with system prompt."""
    prompt = ""
    
    if system_prompt:
        prompt += f"<|system|>\n{system_prompt}</s>\n"
    
    for msg in messages:
        if msg["role"] == "user":
            prompt += f"<|user|>\n{msg['content']}</s>\n"
        elif msg["role"] == "assistant":
            prompt += f"<|assistant|>\n{msg['content']}</s>\n"
    prompt += "<|assistant|>\n"
    return prompt

def truncate_messages(messages, max_messages=10):
    """Keep only the most recent messages to fit within context limit."""
    if len(messages) > max_messages:
        return messages[-max_messages:]
    return messages

def generate_response(model, messages, system_prompt="", max_tokens=256, temperature=0.7):
    """Generate a response from the model."""
    truncated_messages = truncate_messages(messages)
    prompt = format_prompt(truncated_messages, system_prompt)
    
    response = model(
        prompt,
        max_new_tokens=max_tokens,
        temperature=temperature,
        top_p=0.95,
        stop=["</s>", "<|user|>", "<|assistant|>", "<|system|>"]
    )
    
    return response.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = PRESET_PROMPTS["Khisba GIS"]

if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "Khisba GIS"

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = {}

if "active_search_tool" not in st.session_state:
    st.session_state.active_search_tool = None

with st.sidebar:
    st.header("Persona / System Prompt")
    
    selected_preset = st.selectbox(
        "Choose a preset:",
        options=list(PRESET_PROMPTS.keys()),
        index=list(PRESET_PROMPTS.keys()).index(st.session_state.selected_preset),
        key="preset_selector"
    )
    
    if selected_preset != st.session_state.selected_preset:
        st.session_state.selected_preset = selected_preset
        if selected_preset != "Custom":
            st.session_state.system_prompt = PRESET_PROMPTS[selected_preset]
    
    system_prompt = st.text_area(
        "System prompt (customize how the AI responds):",
        value=st.session_state.system_prompt,
        height=150,
        placeholder="Enter instructions for how the AI should behave...",
        key="system_prompt_input"
    )
    
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt
        if system_prompt not in PRESET_PROMPTS.values():
            st.session_state.selected_preset = "Custom"
    
    st.divider()
    
    # Search Tools Section
    st.header("🔍 Search Tools")
    st.caption("Free APIs - No keys required")
    
    # Create columns for search tool buttons
    cols = st.columns(2)
    
    with cols[0]:
        if st.button(f"{SEARCH_TOOLS['ArXiv']['icon']} ArXiv", use_container_width=True):
            st.session_state.active_search_tool = "ArXiv"
            st.rerun()
        
        if st.button(f"{SEARCH_TOOLS['Weather']['icon']} Weather", use_container_width=True):
            st.session_state.active_search_tool = "Weather"
            st.rerun()
    
    with cols[1]:
        if st.button(f"{SEARCH_TOOLS['DuckDuckGo']['icon']} DuckDuckGo", use_container_width=True):
            st.session_state.active_search_tool = "DuckDuckGo"
            st.rerun()
        
        if st.button(f"{SEARCH_TOOLS['Wikipedia']['icon']} Wikipedia", use_container_width=True):
            st.session_state.active_search_tool = "Wikipedia"
            st.rerun()
    
    # Search input
    if st.session_state.active_search_tool:
        st.divider()
        st.subheader(f"{SEARCH_TOOLS[st.session_state.active_search_tool]['icon']} {SEARCH_TOOLS[st.session_state.active_search_tool]['name']}")
        
        search_query = st.text_input(
            "Search query:",
            key="search_input",
            placeholder=f"Enter your {SEARCH_TOOLS[st.session_state.active_search_tool]['name'].lower()} search..."
        )
        
        if st.button("Search", use_container_width=True):
            if search_query:
                with st.spinner(f"Searching {SEARCH_TOOLS[st.session_state.active_search_tool]['name']}..."):
                    if st.session_state.active_search_tool == "ArXiv":
                        st.session_state.search_results = search_arxiv(search_query)
                    elif st.session_state.active_search_tool == "DuckDuckGo":
                        st.session_state.search_results = search_duckduckgo(search_query)
                    elif st.session_state.active_search_tool == "Weather":
                        st.session_state.search_results = get_weather(search_query)
                    elif st.session_state.active_search_tool == "Wikipedia":
                        st.session_state.search_results = search_wikipedia(search_query)
                st.rerun()
        
        if st.button("Close Search", type="secondary", use_container_width=True):
            st.session_state.active_search_tool = None
            st.rerun()
    
    st.divider()
    st.header("Model Settings")
    temperature = st.slider("Temperature", 0.1, 2.0, 0.7, 0.1, 
                           help="Higher = more creative, Lower = more focused")
    max_tokens = st.slider("Max Tokens", 64, 1024, 256, 64,
                          help="Maximum length of the response")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("Reset Prompt", type="secondary", use_container_width=True):
            st.session_state.system_prompt = PRESET_PROMPTS["Default Assistant"]
            st.session_state.selected_preset = "Default Assistant"
            st.rerun()
    
    st.divider()
    st.caption("Model: TinyLLaMA 1.1B Chat v1.0")
    st.caption("Quantization: Q4_K_M (~637 MB)")

# Main chat area
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🦙 TinyLLaMA Chat")
with col2:
    if st.session_state.active_search_tool:
        st.info(f"🔍 {SEARCH_TOOLS[st.session_state.active_search_tool]['icon']} {SEARCH_TOOLS[st.session_state.active_search_tool]['name']}")

# Display search results if available
if st.session_state.search_results and st.session_state.active_search_tool:
    with st.expander(f"{SEARCH_TOOLS[st.session_state.active_search_tool]['icon']} Search Results", expanded=True):
        if st.session_state.active_search_tool == "ArXiv":
            for i, paper in enumerate(st.session_state.search_results, 1):
                st.markdown(f"**{i}. {paper.get('title', 'No title')}**")
                st.markdown(f"*Authors:* {paper.get('authors', 'Unknown')}")
                st.markdown(f"*Summary:* {paper.get('summary', 'No summary')}")
                st.divider()
        
        elif st.session_state.active_search_tool == "DuckDuckGo":
            if 'abstract' in st.session_state.search_results:
                st.markdown(f"**Abstract:** {st.session_state.search_results['abstract']}")
            if 'related' in st.session_state.search_results:
                st.markdown("**Related Topics:**")
                for topic in st.session_state.search_results['related']:
                    st.markdown(f"- {topic}")
        
        elif st.session_state.active_search_tool == "Weather":
            if 'current_condition' in st.session_state.search_results:
                current = st.session_state.search_results['current_condition'][0]
                st.markdown(f"**🌡️ Temperature:** {current.get('temp_C', 'N/A')}°C")
                st.markdown(f"**💨 Wind:** {current.get('windspeedKmph', 'N/A')} km/h")
                st.markdown(f"**💧 Humidity:** {current.get('humidity', 'N/A')}%")
                st.markdown(f"**🌧️ Precipitation:** {current.get('precipMM', 'N/A')} mm")
        
        elif st.session_state.active_search_tool == "Wikipedia":
            for i, article in enumerate(st.session_state.search_results, 1):
                st.markdown(f"**{i}. {article.get('title', 'No title')}**")
                st.markdown(f"{article.get('snippet', 'No snippet')}...")
                st.divider()
        
        # Button to use search result in chat
        if st.button("Use in Chat", key="use_search_result"):
            summary = ""
            if st.session_state.active_search_tool == "ArXiv":
                summary = f"ArXiv search results: {len(st.session_state.search_results)} papers found."
            elif st.session_state.active_search_tool == "DuckDuckGo":
                summary = f"DuckDuckGo search completed with results."
            elif st.session_state.active_search_tool == "Weather":
                summary = f"Weather data retrieved."
            elif st.session_state.active_search_tool == "Wikipedia":
                summary = f"Wikipedia search: {len(st.session_state.search_results)} articles found."
            
            st.session_state.messages.append({
                "role": "user", 
                "content": f"Here are my {SEARCH_TOOLS[st.session_state.active_search_tool]['name']} search results: {summary}"
            })
            st.session_state.search_results = {}
            st.session_state.active_search_tool = None
            st.rerun()

with st.spinner("Loading TinyLLaMA model... This may take a moment on first run."):
    try:
        model = load_model()
        st.session_state.model_loaded = True
    except Exception as e:
        st.error(f"Failed to load model: {str(e)}")
        st.stop()

if st.session_state.model_loaded:
    st.success("Model loaded and ready!", icon="✅")

if st.session_state.system_prompt:
    with st.expander("Current Persona", expanded=False):
        st.info(st.session_state.system_prompt)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Send a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(
                model,
                st.session_state.messages,
                system_prompt=st.session_state.system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
