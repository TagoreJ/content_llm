# streamlit_news_cloud.py
import streamlit as st
import requests

st.set_page_config(page_title="📰 News Explorer", layout="wide")
st.title("📰 News Explorer")

# --- NewsAPI Config ---
NEWS_API_KEY = "YOUR_NEWSAPI_KEY"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# --- Sidebar Filters ---
st.sidebar.header("Filters")
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
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        st.error(f"Failed to fetch news. Status code: {response.status_code}")
        return []

# --- Get News ---
articles = fetch_news(NEWS_API_KEY, country, category, search_query)

if not articles:
    st.warning("No news found for the selected filters or search.")
else:
    # Display each news article
    for article in articles:
        st.markdown(f"### [{article['title']}]({article['url']})")
        if article.get("urlToImage"):
            st.image(article['urlToImage'], use_column_width=True)
        st.write(article.get("description", ""))
        st.markdown("---")
