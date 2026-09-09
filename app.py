import streamlit as st
import os
import re
import base64
from duckduckgo_search import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

# Load local .env file if available
load_dotenv()

st.set_page_config(page_title="VEO 3 AI Reel Prompt Generator", page_icon="🎬", layout="wide")

# Pre-configured API Key (Base64 Decoded automatically at runtime)
DEFAULT_KEY_B64 = "QVEuQWI4Uk42SzZUb0hFWXR2LW1rNFBjU0hHQWc4OVVGTFk3emwtanEzZ1JhSUlZcXZjVEE="
DEFAULT_KEY = base64.b64decode(DEFAULT_KEY_B64).decode()

# Sidebar API Key Configuration
with st.sidebar:
    st.header("🔑 Gemini API Key Configuration")
    user_key_input = st.text_input("Gemini API Key (starts with AIzaSy...):", value="", type="password", placeholder="Paste your API key here...")
    st.info("💡 Get your free API Key in 10 seconds from [aistudio.google.com](https://aistudio.google.com/)")

# Determine active API Key
GEMINI_API_KEY = user_key_input.strip() or os.getenv("GEMINI_API_KEY") or (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets else None) or DEFAULT_KEY

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        pass

# Custom UI Styling
st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; border-radius: 10px; }
    .stButton button { background-color: #FF4B4B; color: white; font-size: 18px; font-weight: bold; border-radius: 8px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 1-Click VEO 3 Master Reel Prompt Generator")
st.caption("केवल अपनी स्क्रिप्ट पेस्ट करें — लोकेशन रिसर्च, 8-सेकंड ElevenLabs टाइमिंग, और VEO3 प्रॉम्प्ट्स 100% ऑटोमैटिक!")

# Single Input: Script
user_script = st.text_area("✍️ अपनी स्क्रिप्ट यहाँ पेस्ट करें (Paste Your Script Here):", height=220, placeholder="यहाँ अपनी पूरी स्क्रिप्ट (हिंदी/English) पेस्ट करें...")

def research_location(text):
    """Automatic web research for location architecture & reference image links."""
    results = []
    try:
        with DDGS() as ddgs:
            query_str = text[:120].replace('\n', ' ')
            search_results = list(ddgs.text(f"{query_str} wikipedia architecture image link", max_results=3))
            for r in search_results:
                results.append(f"- {r.get('title')}: {r.get('body')} (Link: {r.get('href')})")
    except Exception:
        results.append("Standard historical architecture reference mode active.")
    return "\n".join(results) if results else "Standard reference mode."

def calculate_scenes(script_text):
    """Auto-calculate optimal duration and 8-second scenes count based on ElevenLabs Hindi speech speed (~2.5 words/sec)."""
    words = len(re.findall(r'\w+', script_text))
    estimated_seconds = max(16, int(words / 2.6))
    scenes_count = max(2, round(estimated_seconds / 8))
    total_duration = scenes_count * 8
    return words, total_duration, scenes_count

def generate_with_best_model(prompt_text):
    """Dynamically discover available models and fallback gracefully."""
    available_model_names = []
    try:
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace('models/', '')
                available_model_names.append(name)
    except Exception:
        available_model_names = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-pro']

    # Priority list
    target_candidates = ['gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-pro']
    model_queue = []
    for cand in target_candidates:
        for av in available_model_names:
            if cand in av:
                if av not in model_queue:
                    model_queue.append(av)
    for av in available_model_names:
        if av not in model_queue:
            model_queue.append(av)

    if not model_queue:
        model_queue = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']

    last_err = None
    for m_name in model_queue:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt_text)
            return response.text, m_name
        except Exception as e:
            last_err = e
            continue
    raise Exception(f"{last_err}")

if st.button("🚀 जनरेट करें (Generate VEO 3 Prompts)", use_container_width=True):
    if not user_script.strip():
        st.warning("⚠️ कृपया पहले अपनी स्क्रिप्ट पेस्ट करें!")
    else:
        words_count, total_duration, scenes_count = calculate_scenes(user_script)
        
        st.success(f"📊 ऑटो-डिटेक्टेड: **{words_count} शब्द** | कुल लम्बाई: **{total_duration} सेकंड** | सीन्स: **{scenes_count} सीन्स** (8s प्रति सीन)")
        
        with st.spinner("🔍 लोकेशन की ऑटो-रिसर्च और वास्तुकला डिटेल्स निकाली जा रही हैं..."):
            research_info = research_location(user_script)
        
        with st.spinner("🎬 AI द्वारा प्रॉम्प्ट्स जनरेट हो रहे हैं..."):
            prompt_instruction = f"""
            You are a master AI Video Producer specializing in Google VEO 3, Midjourney, and 8-second multi-scene video reels.

            INPUT SCRIPT:
            "{user_script}"

            AUTOMATIC WEB RESEARCHED LOCATION & ARCHITECTURE LINKS:
            {research_info}

            AUTO-CALCULATED REEL SPECIFICATIONS:
            - Total Words: {words_count} words
            - Target Duration: {total_duration} Seconds
            - Number of Scenes: Exactly {scenes_count} Scenes (8 Seconds per scene)

            CRITICAL AUTOMATION RULES:
            1. Divide the script evenly into exactly {scenes_count} parts (~20-25 words per 8-second scene).
            2. For EVERY scene (Scene 1 to Scene {scenes_count}), you MUST output:
               - **VO Line**: The exact Hindi script portion for this 8s segment.
               - **🖼️ First-frame image prompt**: Midjourney/ChatGPT style prompt containing exact location details + reference URLs from research.
               - **🖼️ Last-frame image prompt**: Midjourney/ChatGPT style prompt ensuring 0-cut visual handoff to the next scene.
               - **🎬 VEO3 video prompt**: Detailed VEO 3 prompt covering SUBJECT, SETTING, FRAMING, OBJECT DISAMBIGUATION, SCENE LAYOUT, MOTION ARC (0-8s), CAMERA, LIGHTING & COLOR, VOICEOVER SYNC, PERFORMANCE/EMOTION, PRODUCT DETAIL, ON-SCREEN TEXT, SOUND, and HANDOFF.

            Format the entire output in clean markdown.
            """

            try:
                result_markdown, model_used = generate_with_best_model(prompt_instruction)
                
                st.info(f"✨ AI मॉडल: **{model_used}** द्वारा जनरेट किया गया।")
                st.markdown("---")
                st.markdown("### 🍿 आपकी रील का पूरा प्रॉडक्शन सेट तैयार है:")
                st.markdown(result_markdown)
                
                st.download_button(
                    label="💾 All Prompts Download (.md)",
                    data=result_markdown,
                    file_name="veo3_multi_scene_prompts.md",
                    mime="text/markdown"
                )
            except Exception as err:
                st.error(f"❌ Error generating prompts: {err}")
                st.warning("👉 **सलाह:** यदि आप अपनी खुद की API Key लगाना चाहते हैं, तो साइडबार (Left Sidebar) में अपनी मुफ़्त Gemini API Key (`AIzaSy...`) पेस्ट करें। [aistudio.google.com](https://aistudio.google.com/) से 10 सेकंड में मुफ़्त Key मिल जाती है।")
