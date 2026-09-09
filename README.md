# 🎬 VEO 3 Multi-Scene Reel Prompt Generator

An automated AI tool that takes any video script (Hindi/Hinglish/English), researches real location architecture & image reference links via web search, splits the script into 8-second scenes based on ElevenLabs voice speed, and generates production-ready **First Frame Image Prompts**, **Last Frame Image Prompts**, and **Google VEO 3 Video Prompts** with 0-cut handoff.

---

## 🌟 Features
- **Location Auto-Research**: Searches DuckDuckGo for Wikipedia links and official architectural image URLs.
- **ElevenLabs Voice Timing**: Automatically splits scripts into 8s scenes (~20-25 words per scene).
- **0-Cut Handoff Guarantee**: Scene-to-scene visual & camera position continuity.
- **VEO 3 Production Specs**: Includes Motion Arc, Camera Direction, Lighting, Audio Sync, On-Screen Text, and Sound FX.

---

## 🚀 Quick Setup (Local Machine)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/veo3-prompt-generator.git
   cd veo3-prompt-generator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Enter your Gemini API Key** in the sidebar and paste any script to generate your prompts!

---

## 🌐 Deploy to GitHub & Streamlit Community Cloud (Free for Anyone to Use)

To host this online so **anyone** can use it without installing Python:

1. Create a public repository on GitHub and push all files (`app.py`, `requirements.txt`, `README.md`).
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub repository and set Main File Path to `app.py`.
4. Click **Deploy**! Your web app link will be live for everyone.
