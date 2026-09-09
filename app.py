import streamlit as st
import os
import re
from duckduckgo_search import DDGS
import google.generativeai as genai
from dotenv import load_dotenv

# Load local .env file automatically
load_dotenv()

st.set_page_config(page_title="VEO 3 AI Reel Prompt Generator", page_icon="🎬", layout="wide")

# Fetch API Key automatically from .env, environment, or Streamlit Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets else None)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Custom UI Styling
st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; border-radius: 10px; }
    .stButton button { background-color: #FF4B4B; color: white; font-size: 18px; font-weight: bold; border-radius: 8px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 1-Click VEO 3 Master Reel Prompt Generator")
st.caption("केवल अपनी स्क्रिप्ट पेस्ट करें — लोकेशन रिसर्च, 8-सेकंड ElevenLabs टाइमिंग, और VEO3 प्रॉम्प्ट्स 100% ऑटोमैटिक!")

# Single Input: Only Script!
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
    except Exception as e:
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
    """Try top Gemini models in order of capability: gemini-1.5-pro -> gemini-2.0-flash -> gemini-1.5-flash."""
    models_to_try = ['gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash']
    last_err = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_text)
            return response.text, model_name
        except Exception as e:
            last_err = e
            continue
    raise Exception(f"All models failed. Last error: {last_err}")

if st.button("🚀 जनरेट करें (Generate VEO 3 Prompts)", use_container_width=True):
    if not user_script.strip():
        st.warning("⚠️ कृपया पहले अपनी स्क्रिप्ट पेस्ट करें!")
    elif not GEMINI_API_KEY:
        st.error("🔑 GEMINI_API_KEY लोड नहीं हुई है। कृपया .env फ़ाइल या Streamlit Secrets चेक करें।")
    else:
        words_count, total_duration, scenes_count = calculate_scenes(user_script)
        
        st.success(f"📊 ऑटो-डिटेक्टेड: **{words_count} शब्द** | कुल लम्बाई: **{total_duration} सेकंड** | सीन्स: **{scenes_count} सीन्स** (8s प्रति सीन)")
        
        with st.spinner("🔍 लोकेशन की ऑटो-रिसर्च और वास्तुकला डिटेल्स निकाली जा रही हैं..."):
            research_info = research_location(user_script)
        
        with st.spinner("🎬 सर्वश्रेष्ठ AI मॉडल (Gemini 1.5 Pro) द्वारा प्रॉम्प्ट्स जनरेट हो रहे हैं..."):
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
