import streamlit as st
from GoogleNews import GoogleNews
from PIL import Image
import requests
from io import BytesIO

# ----------------------
# PAGE SETUP
# ----------------------
st.set_page_config(page_title="Live News Hub", layout="wide")
st.title("📰 Live News Hub")
st.write("Get the latest news and search for topics in real-time!")

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

# ----------------------
# NEWS DISPLAY
# ----------------------
placeholder_image = "https://via.placeholder.com/150x100.png?text=No+Image"

if news_list:
    # Display in 3 columns like Google News
    num_cols = 3
    cols = st.columns(num_cols)

    for i, news in enumerate(news_list[:15]):  # Show max 15 news
        col = cols[i % num_cols]

        # Try to get image
        image_url = news.get("img") or placeholder_image
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
        except:
            img = Image.open(BytesIO(requests.get(placeholder_image).content))

        col.image(img, use_column_width=True)
        col.markdown(f"**{news.get('title', 'No Title')}**")
        col.write(news.get('desc', 'No Description'))
        col.write(f"🗓️ {news.get('date', 'No Date')}")
        col.markdown(f"[Read more]({news.get('link', '#')})")
        col.write("---")
else:
    st.write("No news found for this topic.")

# ----------------------
# FOOTER
# ----------------------
st.write("Powered by Google News | Placeholder images for missing thumbnails")
