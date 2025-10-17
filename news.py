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
    googlenews.get_news('Top Stories')

news_list = googlenews.result()
placeholder_image = "https://via.placeholder.com/300x180.png?text=No+Image"

# ----------------------
# CSS STYLING (DARK CARDS)
# ----------------------
st.markdown("""
<style>
.news-card {
    background-color: #1e1e1e;
    color: #f0f0f0;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.news-card:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}
.news-title {
    font-weight: bold;
    font-size: 18px;
    color: #ffffff;
    margin-top: 5px;
}
.news-desc {
    font-size: 14px;
    color: #cccccc;
    margin-top: 5px;
}
.news-date {
    font-size: 12px;
    color: #aaaaaa;
    margin-top: 5px;
}
a {
    color: #1e90ff;
    text-decoration: none;
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

        # Extract title and date safely
        title = news.get("title") or "No Title"
        date = news.get("date") or "No Date"
        desc = news.get("desc") or "Click Read More"

        # Image (placeholder for now)
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
            <div class="news-title">{title}</div>
            <div class="news-desc">{desc}</div>
            <div class="news-date">🗓️ {date}</div>
            <a href="{news.get('link','#')}" target="_blank">Read more</a>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("<p>No news found for this topic.</p>", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; margin-top:50px;'>Powered by Google News | Placeholder images for missing thumbnails</p>", unsafe_allow_html=True)
