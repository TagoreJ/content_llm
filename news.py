import streamlit as st
import requests
import time
import random
from bs4 import BeautifulSoup

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="📰 News + AI Writer", layout="wide")
st.title("📰 News + ✨ AI Content Creator")

# ===============================
# API KEYS
# ===============================
try:
    NEWS_API_KEY = st.secrets["newsapi"]["key"]
    GOOGLE_AI_KEY = st.secrets["googleai"]["key"]
except Exception:
    st.error("❌ API keys not found in Streamlit Secrets! Please add [newsapi] and [googleai] keys.")
    st.stop()

# ===============================
# TABS
# ===============================
tab1, tab2 = st.tabs(["🗞️ News Explorer", "✍️ AI Content Generator"])

# ===============================
# TAB 1: NEWS EXPLORER
# ===============================
with tab1:
    st.subheader("🌍 Explore Latest Headlines")

    with st.sidebar:
        st.header("Filters")
        country = st.selectbox("Select Country", ["us", "in", "gb", "ca", "au"], index=1)
        category = st.selectbox(
            "Select Category",
            ["business", "entertainment", "general", "health", "science", "sports", "technology"]
        )
        search_query = st.text_input("Search News (optional)")
        fetch_button = st.button("🔍 Fetch News")

    def fetch_news(api_key, country, category, query):
        params = {
            "apiKey": api_key,
            "country": country,
            "category": category,
            "q": query if query else None,
            "pageSize": 20
        }
        url = "https://newsapi.org/v2/top-headlines"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("articles", [])
        elif response.status_code == 401:
            st.error("🚫 Unauthorized! Check your NewsAPI key.")
            return []
        elif response.status_code == 429:
            st.error("⚠️ Rate limit exceeded! Free plan allows 100 requests/day.")
            return []
        else:
            st.error(f"❌ Failed to fetch news. Status code: {response.status_code}")
            return []

    if fetch_button:
        progress = st.progress(0)
        status = st.empty()
        status.text("🔍 Checking API connection...")

        time.sleep(0.5)
        progress.progress(20)
        status.text("📰 Fetching latest news...")

        articles = fetch_news(NEWS_API_KEY, country, category, search_query)

        progress.progress(70)
        status.text("📄 Formatting news...")
        time.sleep(0.5)

        progress.progress(100)
        status.text("✅ Done!")

        if not articles:
            st.warning("No news found for the selected filters or search.")
        else:
            st.success(f"✅ Found {len(articles)} news articles.")
            st.session_state["latest_articles"] = articles
            st.session_state["selected_category"] = category

            for article in articles:
                st.markdown(f"### [{article['title']}]({article['url']})")
                if article.get("urlToImage"):
                    st.image(article["urlToImage"], use_column_width=True)
                st.write(article.get("description", ""))
                st.caption(f"🗞️ Source: {article.get('source', {}).get('name', 'Unknown')}")
                st.markdown("---")

# ===============================
# TAB 2: AI CONTENT GENERATOR
# ===============================
with tab2:
    st.subheader("✍️ Generate Professional Posts from News")

    if "latest_articles" not in st.session_state or not st.session_state["latest_articles"]:
        st.info("ℹ️ Please fetch news first from the 'News Explorer' tab.")
    else:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_AI_KEY)

        article_titles = [a["title"] for a in st.session_state["latest_articles"]]
        selected_title = st.selectbox("🗞️ Select a news article to generate content", article_titles)

        # ✅ Auto-detect tone based on category
        category = st.session_state.get("selected_category", "general")
        tone_map = {
            "business": "Professional",
            "entertainment": "Creative",
            "health": "Informative",
            "science": "Analytical",
            "sports": "Motivational",
            "technology": "Innovative",
            "general": "Neutral"
        }
        detected_tone = tone_map.get(category, "Professional")

        st.markdown(f"🧭 **Detected tone:** `{detected_tone}` based on category `{category}`")
        word_limit = st.slider("📏 Word Limit", 100, 400, 200)

        if st.button("✨ Generate Content"):
            progress = st.progress(0)
            status = st.empty()
            status.text("🔗 Connecting to Google AI...")

            model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

            chosen_article = next((a for a in st.session_state["latest_articles"] if a["title"] == selected_title), None)

            prompt = f"""
            You are a professional content writer. Based on the following news article:
            Title: {chosen_article['title']}
            Description: {chosen_article.get('description', '')}

            Write a {detected_tone.lower()} LinkedIn post or blog introduction (around {word_limit} words)
            that sounds natural, engaging, and reader-friendly.
            """

            progress.progress(40)
            status.text("🧠 Generating content using Google AI...")

            try:
                ai_response = model.generate_content(prompt)
                ai_text = ai_response.text
            except Exception as e:
                st.error(f"Error generating content: {e}")
                ai_text = ""

            progress.progress(80)
            status.text("🖼️ Finding a matching free image...")

            query = selected_title.split()[0]
            img_url = f"https://source.unsplash.com/800x400/?{query},{category}"
            time.sleep(1)

            progress.progress(100)
            status.text("✅ Done!")

            if ai_text:
                st.image(img_url, use_column_width=True)
                st.markdown("### ✍️ Generated Post:")
                st.write(ai_text)
                st.success("✅ Ready to post on LinkedIn or Blog!")
