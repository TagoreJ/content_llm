# streamlit_news_ai.py
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="📰 News & AI Content", layout="wide")

st.title("📰 News Explorer & AI Content Generator")

# --- Tabs ---
tab1, tab2 = st.tabs(["News Explorer", "AI Content Generator"])

# =============================
# --- Tab 1: News Explorer ----
# =============================
with tab1:
    st.header("News Explorer")

    # --- Fetch NewsAPI Key ---
    try:
        NEWS_API_KEY = st.secrets["newsapi"]["key"]
    except Exception:
        st.error("API key not found! Add it in Streamlit Secrets as [newsapi] key.")
        st.stop()

    # --- Sidebar Filters ---
    st.sidebar.header("News Filters")
    country = st.sidebar.selectbox("Select Country", ["us", "in", "gb", "ca", "au"], index=1)
    category = st.sidebar.selectbox(
        "Select Category",
        ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    )
    search_query = st.sidebar.text_input("Search News (optional)")

    # --- Fetch News Function ---
    def fetch_news(api_key, country, category, query):
        params = {
            "apiKey": api_key,
            "country": country,
            "category": category,
            "q": query if query else None,
            "pageSize": 30
        }
        try:
            response = requests.get("https://newsapi.org/v2/top-headlines", params=params)
            if response.status_code == 200:
                return response.json().get("articles", [])
            else:
                st.error(f"Failed to fetch news. Status code: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return []

    # --- Get News ---
    articles = fetch_news(NEWS_API_KEY, country, category, search_query)

    if not articles:
        st.warning("No news found for the selected filters or search.")
    else:
        for article in articles:
            st.markdown(f"### [{article['title']}]({article['url']})")
            if article.get("urlToImage"):
                st.image(article['urlToImage'], use_column_width=True)
            st.write(article.get("description", ""))
            st.markdown("---")

# ======================================
# --- Tab 2: AI Content Generator ----
# ======================================
with tab2:
    st.header("AI Content Generator")
    
    # --- Google AI Studio Key ---
    try:
        GOOGLE_AI_KEY = st.secrets["googleai"]["key"]
    except Exception:
        st.error("Google AI Studio API key not found! Add it in Streamlit Secrets as [googleai] key.")
        st.stop()

    # --- Input Section ---
    st.subheader("Generate Content from News")
    selected_article = st.selectbox(
        "Select a news article to base your content on",
        [f"{a['title']}" for a in articles] if articles else ["No news available"]
    )
    post_type = st.selectbox("Content Type", ["Social Media Post", "Blog Post", "Newsletter"])
    generate_button = st.button("Generate AI Content")

    # --- Function to fetch AI-generated content ---
    def generate_ai_content(article_title, post_type):
        """
        Example using Google Generative AI Studio API (pseudo-code)
        """
        prompt = f"""
        You are a professional content writer. 
        Create a {post_type} based on this news: "{article_title}".
        Make it engaging, professional, and ready to post. 
        Include headings, bullet points if needed.
        """
        # Call Google AI API (pseudo-code, replace with real request)
        # Example:
        # response = requests.post(
        #     "https://api.generativeai.googleapis.com/v1beta2/models/text-bison-001:generate",
        #     headers={"Authorization": f"Bearer {GOOGLE_AI_KEY}"},
        #     json={"prompt": prompt, "max_output_tokens": 500}
        # )
        # content = response.json()["candidates"][0]["content"]
        content = f"Generated {post_type} content based on news: {article_title}"  # Placeholder
        return content

    if generate_button and articles:
        ai_content = generate_ai_content(selected_article, post_type)
        st.subheader("Generated Content")
        st.write(ai_content)

        # --- Optional: Fetch free images from web ---
        st.subheader("Suggested Free Image")
        query = " ".join(selected_article.split()[:5])  # Take first 5 words
        search_url = f"https://www.pexels.com/search/{query}/"
        try:
            res = requests.get(search_url)
            soup = BeautifulSoup(res.text, "html.parser")
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                st.image(img_tag["src"], caption="Suggested image from Pexels", use_column_width=True)
        except:
            st.warning("Could not fetch free image automatically.")

