import streamlit as st
import requests
import time
from bs4 import BeautifulSoup
import random

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(page_title="📰 News + AI Writer", layout="wide")
st.title("📰 News + ✨ AI Content Creator")

# ===============================
# LOAD API KEYS
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

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        country = st.selectbox("Select Country", ["us", "in", "gb", "ca", "au"], index=1)
        category = st.selectbox(
            "Select Category",
            ["business", "entertainment", "general", "health", "science", "sports", "technology"]
        )
        search_query = st.text_input("Search News (optional)")
        if st.button("🔍 Fetch News"):
            st.session_state["fetch_trigger"] = True
        else:
            st.session_state["fetch_trigger"] = False

    def fetch_news(api_key, country, category, query):
        """Fetch news from NewsAPI"""
        params = {
            "apiKey": api_key,
            "country": country,
            "category": category,
            "q": query if query else None,
            "pageSize": 20
        }
        url = "https://newsapi.org/v2/top-headlines"
        with st.spinner("📰 Fetching the latest news..."):
            response = requests.get(url, params=params)
            time.sleep(1.5)
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

    if st.session_state.get("fetch_trigger"):
        with st.progress(0, text="Starting fetch...") as progress:
            progress.progress(20, text="🔍 Checking API connection...")
            time.sleep(0.5)
            articles = fetch_news(NEWS_API_KEY, country, category, search_query)
            progress.progress(70, text="📄 Formatting news...")
            time.sleep(0.8)
            progress.progress(100, text="✅ Done!")

        if not articles:
            st.warning("No news found for the selected filters or search.")
        else:
            for article in articles:
                st.markdown(f"### [{article['title']}]({article['url']})")
                if article.get("urlToImage"):
                    st.image(article["urlToImage"], use_column_width=True)
                st.write(article.get("description", ""))
                st.caption(f"🗞️ Source: {article.get('source', {}).get('name', 'Unknown')}")
                st.markdown("---")

            # Save for AI Content tab
            st.session_state["latest_articles"] = articles

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

        tone = st.selectbox("✏️ Choose Writing Style", ["Professional", "Engaging", "Informative", "Creative"])
        word_limit = st.slider("📏 Word Limit", 100, 400, 200)

        if st.button("✨ Generate Content"):
            progress = st.progress(0, text="Connecting to Google AI...")
            time.sleep(1)
            model = genai.GenerativeModel("gemini-1.5-flash")

            chosen_article = next((a for a in st.session_state["latest_articles"] if a["title"] == selected_title), None)
            content_prompt = f"""
            You are a professional content writer. Based on the following news article:
            Title: {chosen_article['title']}
            Description: {chosen_article.get('description', '')}
            
            Write a {tone.lower()} LinkedIn post or blog introduction (around {word_limit} words)
            that sounds natural, professional, and reader-friendly.
            """

            progress.progress(40, text="🧠 Generating content using AI...")
            try:
                ai_response = model.generate_content(content_prompt)
                ai_text = ai_response.text
            except Exception as e:
                st.error(f"Error generating content: {e}")
                ai_text = ""

            progress.progress(80, text="🖼️ Finding a matching image...")
            # Get a random free image
            query = selected_title.split()[0]
            img_url = f"https://source.unsplash.com/800x400/?{query},{category}"
            time.sleep(1)
            progress.progress(100, text="✅ Done!")

            if ai_text:
                st.image(img_url, use_column_width=True)
                st.markdown("### ✍️ Generated Post:")
                st.write(ai_text)
                st.success("✅ Ready to post on LinkedIn or Blog!")
