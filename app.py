from flask import Flask, render_template, redirect, request
from urllib.parse import urlparse
from db import get_bookmarks, get_bookmark, get_all_folders, get_all_tags, create_bookmark, delete_bookmark

app = Flask(__name__)

@app.route("/")
def index():
    bookmarks = get_bookmarks()
    folders = get_all_folders()
    tags = get_all_tags()
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags
    )

@app.route("/grid")
def grid():
    bookmarks = get_bookmarks()
    folders = get_all_folders()
    tags = get_all_tags()
    return render_template("grid.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags
    )

@app.route("/bookmark/<int:id>")
def reading(id):
    bookmark = get_bookmark(id)
    if not bookmark:
        return "Bookmark not found", 404
    folders = get_all_folders()
    tags = get_all_tags()
    return render_template("reading.html",
        bookmark=bookmark,
        folders=folders,
        tags=tags
    )

@app.route("/bookmarks", methods=["POST"])
def add_bookmark():
    url = request.form.get("url")
    if not url:
        return "URL required", 400

    domain = urlparse(url).netloc

    create_bookmark({
        "url": url,
        "domain": domain,
        "title": None,
        "description": None,
        "author": None,
        "content": None,
        "image_url": None,
        "favicon_url": None,
        "published": None,
        "word_count": 0,
        "site_name": None,
        "language": None,
        "read_time": 0,
        "canonical_url": None,
    })

    return redirect("/")

@app.route("/bookmark/<int:id>/favorite", methods=["POST"])
def toggle_favorite_route(id):
    toggle_favorite(id)
    return redirect(request.referrer or "/")

@app.route("/bookmark/<int:id>/delete", methods=["POST"])
def delete_bookmark_route(id):
    delete_bookmark(id)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")