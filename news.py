import streamlit as st
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup

# --- Streamlit Config ---
st.set_page_config(page_title="📰 AI News & Content Studio", layout="wide")
st.title("📰 AI News & Content Studio")
st.write("Fetch the latest news, and let AI craft professional content posts for you!")

# --- Load API Keys from Secrets ---
try:
    NEWS_API_KEY = st.secrets["newsapi"]["key"]
    GOOGLE_AI_KEY = st.secrets["googleai"]["key"]
except Exception:
    st.error("❌ API keys not found. Please add them under 'Secrets' in Streamlit Cloud.")
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
    st.sidebar.header("🧭 Filters")
    country = st.sidebar.selectbox("🌎 Country", ["us", "in", "gb", "ca", "au"], index=1)
    category = st.sidebar.selectbox(
        "🗂️ Category",
        ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    )
    search_query = st.sidebar.text_input("🔍 Search News")

    progress = st.progress(0, text="Starting News Fetch...")

    progress.progress(25, text="🔍 Connecting to NewsAPI...")
    articles = fetch_news(NEWS_API_KEY, country, category, search_query)

    progress.progress(60, text="📰 Processing fetched articles...")

    if not articles:
        st.warning("No news found.")
    else:
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['url']})")
            if article.get("urlToImage"):
                st.image(article['urlToImage'], use_column_width=True)
            st.write(article.get("description", ""))
            st.markdown("---")

    progress.progress(100, text="✅ News Loaded Successfully!")

    # Store top 3 headlines for AI use
    st.session_state["top_headlines"] = [a["title"] for a in articles[:3]] if articles else []


# --- Tab 2: AI Content Generator ---
with tab2:
    st.header("🧠 AI Content Generator")
    st.write("Generate content ideas based on any topic or from the latest news.")

    news_topic = st.text_input("Enter a topic manually (optional):")

    use_auto = st.checkbox("✨ Use Top 3 Latest Headlines from News Tab")

    if st.button("🚀 Generate AI Content"):
        topics_to_use = []

        if use_auto and "top_headlines" in st.session_state and st.session_state["top_headlines"]:
            topics_to_use = st.session_state["top_headlines"]
            st.info(f"Using top 3 latest headlines: {topics_to_use}")
        elif news_topic:
            topics_to_use = [news_topic]
        else:
            st.warning("Please enter a topic or select the latest headlines option.")
            st.stop()

        progress = st.progress(0, text="🤖 Connecting to Gemini AI...")

        try:
            model = genai.GenerativeModel("gemini-2.0-flash")  # ✅ Works with free-tier
            all_outputs = []

            for idx, topic in enumerate(topics_to_use):
                progress.progress((idx + 1) * 30, text=f"✨ Generating content for: {topic}...")

                prompt = f"""
                You are a professional social media content strategist.
                Based on the topic or headline: "{topic}",
                generate:
                1. A short 2-3 line engaging summary.
                2. 3 creative post ideas for LinkedIn/Twitter.
                3. 3-5 suitable hashtags.
                4. Suggest a free image URL from Unsplash or Pexels related to this topic.
                Make it professional yet catchy.
                """

                response = model.generate_content(prompt)
                all_outputs.append((topic, response.text))

            progress.progress(100, text="✅ Content Generated Successfully!")

            # --- Display All Outputs ---
            for topic, content in all_outputs:
                st.subheader(f"🗞️ Topic: {topic}")
                st.write(content)

                # Extract free image links
                soup = BeautifulSoup(content, "html.parser")
                links = [a['href'] for a in soup.find_all('a', href=True)
                         if "unsplash" in a['href'] or "pexels" in a['href']]
                if links:
                    st.image(links[0], caption="Suggested Image", use_column_width=True)
                st.markdown("---")

        except Exception as e:
            st.error(f"Error generating content: {e}")
            progress.empty()
