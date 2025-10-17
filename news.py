import streamlit as st
from GoogleNews import GoogleNews
from PIL import Image
import requests
from io import BytesIO

# ----------------------
# PAGE SETUP
# ----------------------
st.set_page_config(page_title="Live News Hub", layout="wide")
st.markdown("<h1 style='text-align:center;'>📰 Live News Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Get the latest news and search for topics in real-time!</p>", unsafe_allow_html=True)

# ----------------------
# SEARCH BAR
# ----------------------
query = st.text_input("🔍 Search for news topic:", "")

# ----------------------
# GOOGLE NEWS FETCH
# ----------------------
googlenews = GoogleNews(lang='en', period='7d')
if query:
    googlenews.search(query)
else:
    googlenews = GoogleNews(lang='en', period='1d')
    googlenews.get_news('Top Stories')

news_list = googlenews.result()
placeholder_image = "https://via.placeholder.com/300x180.png?text=No+Image"

# ----------------------
# CSS STYLING
# ----------------------
st.markdown("""
<style>
.news-card {
    background-color: #f9f9f9;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.news-card:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.news-title {
    font-weight: bold;
    font-size: 18px;
}
.news-desc {
    font-size: 14px;
    color: #333;
}
.news-date {
    font-size: 12px;
    color: #777;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# NEWS DISPLAY
# ----------------------
if news_list:
    num_cols = 3
    cols = st.columns(num_cols)

    for i, news in enumerate(news_list[:15]):  # Show max 15 news
        col = cols[i % num_cols]

        # Image
        image_url = news.get("img") or placeholder_image
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
        except:
            response = requests.get(placeholder_image)
            img = Image.open(BytesIO(response.content))

        col.markdown(f"""
        <div class="news-card">
            <img src="{image_url}" width="100%" style="border-radius:10px;">
            <div class="news-title">{news.get('title', 'No Title')}</div>
            <div class="news-desc">{news.get('desc', 'No Description')}</div>
            <div class="news-date">🗓️ {news.get('date', 'No Date')}</div>
            <a href="{news.get('link','#')}" target="_blank">Read more</a>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("<p>No news found for this topic.</p>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; margin-top:50px;'>Powered by Google News | Placeholder images for missing thumbnails</p>", unsafe_allow_html=True)
