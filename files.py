import os
import re
from datetime import date

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text[:80]

def save_article(data):
    os.makedirs("articles", exist_ok=True)

    today = date.today().isoformat()
    slug = slugify(data.get("title") or data.get("domain", "untitled"))
    filename = f"{today}-{slug}.md"
    filepath = os.path.join("articles", filename)

    content = data.get("content") or f"No content extracted.\n\nRead at: {data.get('url')}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: \"{(data.get('title') or '').replace(chr(34), chr(39))}\"\n")
        f.write(f"url: {data.get('url', '')}\n")
        f.write(f"domain: {data.get('domain', '')}\n")
        f.write(f"author: {data.get('author', '')}\n")
        f.write(f"published: {data.get('published', '')}\n")
        f.write(f"saved: {today}\n")
        f.write(f"word_count: {data.get('word_count', 0)}\n")
        f.write(f"read_time: {data.get('read_time', 0)}\n")
        f.write(f"---\n\n")
        f.write(f"# {data.get('title', 'Untitled')}\n\n")
        f.write(content)

    return filepath

def delete_article(filepath):
    if filepath and os.path.exists(filepath):
        os.remove(filepath)