import httpx
import trafilatura
from urllib.parse import urlparse

def minimal_bookmark(url):
    domain = urlparse(url).netloc
    return {
        "url": url,
        "domain": domain,
        "title": domain,
        "description": None,
        "author": None,
        "content": None,
        "image_url": None,
        "favicon_url": f"https://www.google.com/s2/favicons?domain={domain}&sz=64",
        "published": None,
        "word_count": 0,
        "site_name": None,
        "language": None,
        "read_time": 0,
        "canonical_url": url,
    }

def fetch_metadata(url):
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
        html = response.text
    except Exception:
        return minimal_bookmark(url)

    meta = trafilatura.extract_metadata(html)
    content = trafilatura.extract(html)
    domain = urlparse(url).netloc
    word_count = len(content.split()) if content else 0

    return {
        "url": url,
        "domain": domain,
        "title": meta.title if meta else domain,
        "description": meta.description if meta else None,
        "author": meta.author if meta else None,
        "content": content,
        "image_url": meta.image if meta else None,
        "favicon_url": f"https://www.google.com/s2/favicons?domain={domain}&sz=64",
        "published": meta.date if meta else None,
        "word_count": word_count,
        "site_name": meta.sitename if meta else None,
        "language": meta.language if meta else None,
        "read_time": word_count // 200,
        "canonical_url": meta.url if meta else url,
    }