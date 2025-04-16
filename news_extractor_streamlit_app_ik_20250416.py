import streamlit as st
from googlesearch import search
from newspaper import Article
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import datetime

st.set_page_config(page_title="News Extractor", layout="wide")
st.title('📰 Google News Article Extractor ')

# --- Input Keyword ---
query = st.text_input("Enter a search keyword:", "Imran Khan in election")
st.write(f"**Search Keyword:** {query}")
st.write(f"**Search Date:** {datetime.date.today()}")

# --- Function to extract author and publisher ---
def extract_meta_data(url):
    try:
        res = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.content, 'html.parser')
        author = None
        publisher = None

        # Common meta tags for author
        possible_author_tags = [
            {'name': 'author'},
            {'property': 'article:author'},
            {'name': 'dc.creator'},
            {'name': 'byline'},
        ]
        for tag in possible_author_tags:
            meta = soup.find('meta', tag)
            if meta and meta.get('content'):
                author = meta.get('content')
                break

        # Common meta tags for publisher
        possible_publisher_tags = [
            {'property': 'og:site_name'},
            {'name': 'publisher'},
            {'name': 'application-name'}
        ]
        for tag in possible_publisher_tags:
            meta = soup.find('meta', tag)
            if meta and meta.get('content'):
                publisher = meta.get('content')
                break

        # Fallback to domain name
        if not publisher:
            publisher = urlparse(url).netloc

        return author, publisher

    except Exception:
        return None, urlparse(url).netloc

# --- Google Search ---
try:
    urls = list(search(query, num_results=15))
    st.subheader("🔗 Top 15 News URLs:")
    for i, url in enumerate(urls, 1):
        st.write(f"{i}. {url}")
except Exception as e:
    st.error(f"Google search error: {e}")
    st.stop()

# --- Article Extraction ---
st.subheader("📰 Extracted News Articles:")

for i, url in enumerate(urls, 1):
    try:
        article = Article(url)
        article.download()
        article.parse()

        author_fallback, publisher = extract_meta_data(url)

        st.markdown(f"### Article {i}: {article.title}")
        st.markdown(f"**Author(s):** {', '.join(article.authors) if article.authors else author_fallback or 'N/A'}")
        st.markdown(f"**Publisher:** {publisher}")
        st.markdown(f"**Publish Date:** {article.publish_date if article.publish_date else 'N/A'}")
        st.markdown(f"**URL:** [Read full article]({url})")
        st.markdown(f"**Content:**\n\n{article.text}")
        st.markdown("---")

    except Exception as e:
        st.warning(f"❌ Failed to extract article {i} from {url}: {e}")
        st.markdown("---")
