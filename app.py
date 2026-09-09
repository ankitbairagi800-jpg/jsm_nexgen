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
    except Exception:
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
            search_results = list(ddgs.text(f"{query_str} wikipedia architecture image link", max_results=4))
            for r in search_results:
                title = r.get('title', '')
                body = r.get('body', '')
                href = r.get('href', '')
                if href:
                    results.append(f"- Location: {title} | Architecture: {body} | Image URL: {href}")
    except Exception:
        pass
    
    if not results:
        results.append(f"- Location: Historical architecture for {text[:40]} | Image URL: https://en.wikipedia.org/wiki/Special:Search?search={text[:30].replace(' ', '+')}")
    return "\n".join(results)

def calculate_scenes(script_text):
    """Auto-calculate optimal duration and 8-second scenes count based on ElevenLabs Hindi speech speed (~2.5 words/sec)."""
    words = len(re.findall(r'\w+', script_text))
    estimated_seconds = max(16, int(words / 2.6))
    scenes_count = max(2, round(estimated_seconds / 8))
    total_duration = scenes_count * 8
    return words, total_duration, scenes_count

def generate_with_best_model(prompt_text):
    """Dynamically discover available models and fallback gracefully across all Gemini versions."""
    available_model_names = []
    try:
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace('models/', '')
                available_model_names.append(name)
    except Exception:
        pass

    priority_order = [
        'gemini-3.6-flash',
        'gemini-3.5-flash',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-flash-latest',
        'gemini-pro-latest',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]

    model_queue = []
    for cand in priority_order:
        for av in available_model_names:
            if cand in av and av not in model_queue:
                model_queue.append(av)

    if not model_queue:
        model_queue = priority_order

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
        
        with st.spinner("🎬 AI द्वारा विस्तृत प्रॉम्प्ट्स जनरेट हो रहे हैं..."):
            prompt_instruction = f"""
            You are a master AI Video Producer specializing in Google VEO 3, Midjourney, and 8-second multi-scene video reels.

            INPUT SCRIPT:
            "{user_script}"

            RESEARCHED LOCATION ARCHITECTURE & DIRECT REFERENCE IMAGE URLS:
            {research_info}

            REEL DURATION SPECIFICATIONS:
            - Total Words: {words_count} words
            - Target Duration: {total_duration} Seconds
            - Number of Scenes: Exactly {scenes_count} Scenes (8 Seconds per scene)

            CRITICAL MANDATORY PROMPT RULES:
            1. You MUST divide the input script into exactly {scenes_count} scenes.
            2. For EVERY SINGLE SCENE, you MUST write EXTREMELY DETAILED, EXHAUSTIVE PROMPTS (never summarize or shorten).
            3. BOTH the "First-frame image prompt" AND "Last-frame image prompt" MUST explicitly include the exact researched Image URL(s) from the research above!
            4. Follow this EXACT markdown structure for Scene 1 through Scene {scenes_count}:

            ### 📽️ SCENE [X] (00:00s - 08:00s) — [Scene Title]

            **VO Line (ElevenLabs 8s):**
            "[Exact Hindi script text for this 8-second scene]"

            #### 🖼️ First-frame image prompt
            `[Detailed Midjourney/ChatGPT style prompt with exact real architectural details AND exact reference Image URL: (Insert researched URL here). 9:16 vertical aspect ratio, 8k resolution, photorealistic]`

            #### 🖼️ Last-frame image prompt
            `[Detailed Midjourney/ChatGPT style prompt for 0-cut handoff with exact real architectural details AND exact reference Image URL: (Insert researched URL here). 9:16 vertical aspect ratio, 8k resolution, photorealistic]`

            #### 🎬 VEO3 video prompt
            - **SUBJECT:** [Detailed subject and architecture description matching reference URL]
            - **SETTING:** [Environment, location background, navy-teal color grade]
            - **FRAMING:** [0-4s and 4-8s shot framing]
            - **OBJECT DISAMBIGUATION:** [Primary focal anchor vs secondary elements]
            - **SCENE LAYOUT:** [Object placement in vertical 9:16 frame]
            - **MOTION ARC (0-8s):** [Second-by-second breakdown: 0-2s, 2-5s, 5-8s motion]
            - **CAMERA:** [Camera motion specs: dolly, pan, tilt, push-in]
            - **LIGHTING & COLOR:** [Shadows, color grading, highlights]
            - **VOICEOVER:** [Hindi VO line synced with specific timestamp triggers]
            - **PERFORMANCE/EMOTION:** [Mood and tone]
            - **PRODUCT DETAIL:** [Stone/carving/architectural crisp details]
            - **ON-SCREEN TEXT:** [Synced bold Hindi captions]
            - **SOUND:** [Sound effects and music cues]
            - **HANDOFF (end frame):** [Exact description matching the start frame of next scene]

            Produce the COMPLETE, UNUNCATED, FULLY DETAILED response for all {scenes_count} scenes now.
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
