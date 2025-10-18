import streamlit as st
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup

# --- Page Config ---
st.set_page_config(page_title="📰 AI News Explorer", layout="wide")

st.title("📰 AI News Explorer")
st.write("Explore news by category and generate AI-powered content ideas!")

# --- Load Secrets Safely ---
try:
    NEWS_API_KEY = st.secrets["newsapi"]["key"]
    GOOGLE_AI_KEY = st.secrets["googleai"]["key"]
except Exception:
    st.error("❌ API keys missing. Please add them under 'Secrets' in Streamlit Cloud.")
    st.stop()

# --- Configure Gemini ---
genai.configure(api_key=GOOGLE_AI_KEY)

# --- Tabs ---
tab1, tab2 = st.tabs(["🌍 News Feed", "🧠 AI Content Generator"])

# --- Function: Fetch News ---
def fetch_news(api_key, country, category, query):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "country": country,
        "category": category,
        "q": query if query else None,
        "pageSize": 20
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("articles", [])
        elif response.status_code == 401:
            st.error("🚫 Unauthorized! Invalid NewsAPI key.")
        elif response.status_code == 429:
            st.error("⚠️ Rate limit exceeded! (Free plan = 100 requests/day)")
        else:
            st.error(f"❌ API Error: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching news: {e}")
    return []

# --- Tab 1: News Feed ---
with tab1:
    st.sidebar.header("Filters")
    country = st.sidebar.selectbox("Country", ["us", "in", "gb", "ca", "au"], index=1)
    category = st.sidebar.selectbox(
        "Category",
        ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    )
    search_query = st.sidebar.text_input("🔍 Search News")

    progress = st.progress(0, text="Starting...")

    progress.progress(20, text="🔍 Checking NewsAPI connection...")
    articles = fetch_news(NEWS_API_KEY, country, category, search_query)

    progress.progress(80, text="✅ Fetch complete! Displaying news...")
    if not articles:
        st.warning("No news found.")
    else:
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['url']})")
            if article.get("urlToImage"):
                st.image(article['urlToImage'], use_column_width=True)
            st.write(article.get("description", ""))
            st.markdown("---")
    progress.progress(100, text="✅ Done!")

# --- Tab 2: AI Content Generator ---
with tab2:
    st.header("🧠 AI Content Generator")
    st.write("Turn latest news topics into professional content ideas!")

    news_topic = st.text_input("Enter a news topic or keyword (e.g., AI, climate, space):")

    if st.button("✨ Generate AI Content"):
        if not news_topic:
            st.warning("Please enter a topic.")
        else:
            progress = st.progress(0, text="🚀 Connecting to Gemini AI...")
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")  # ✅ free-tier supported
                progress.progress(30, text="🤖 Generating ideas...")

                prompt = f"""
                You are a professional content strategist. Based on the news topic '{news_topic}',
                generate:
                1. A short engaging summary (2-3 lines)
                2. 3 post ideas suitable for LinkedIn or Twitter
                3. Suggested hashtags
                4. A relevant free image URL suggestion (use unsplash.com or pexels.com)
                """

                response = model.generate_content(prompt)
                progress.progress(90, text="📝 Finalizing response...")

                st.subheader("📄 AI Generated Content")
                st.write(response.text)

                # Extract possible image suggestion
                soup = BeautifulSoup(response.text, "html.parser")
                links = [a['href'] for a in soup.find_all('a', href=True) if "unsplash" in a['href'] or "pexels" in a['href']]
                if links:
                    st.image(links[0], caption="Suggested Image", use_column_width=True)
                progress.progress(100, text="✅ Content ready!")

            except Exception as e:
                st.error(f"Error generating content: {e}")
                progress.empty()
