from flask import Flask, render_template, redirect, request, make_response
from urllib.parse import urlparse
from db import get_bookmarks, get_bookmark, get_all_folders, get_all_tags, create_bookmark, delete_bookmark, update_bookmark, create_folder, toggle_archive, toggle_favorite, get_favorites, get_untagged, get_archived
from scraper import fetch_metadata
from files import save_article

def is_htmx():
    return request.headers.get("HX-Request") == "true"

def sidebar_context():
    return {
        "folders": get_all_folders(),
        "tags": get_all_tags()
    }

app = Flask(__name__)

@app.route("/")
def index():
    q = request.args.get("q", "")
    bookmarks = get_bookmarks(q=q)
    folders = get_all_folders()
    tags = get_all_tags()
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
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
    if is_htmx():
        return render_template("partials/bookmark_grid.html",
            bookmarks=bookmarks
        )
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

@app.route("/bookmark/<int:id>/item")
def bookmark_item(id):
    bookmark = get_bookmark(id)
    return render_template("partials/bookmark_item.html", bookmark=bookmark)

@app.route("/bookmarks", methods=["POST"])
def add_bookmark():
    url = request.form.get("url")
    if not url:
        return "URL required", 400

    data = fetch_metadata(url)
    data["article_path"] = save_article(data)
    bookmark_id = create_bookmark(data)

    if is_htmx():
        bookmark = get_bookmark(bookmark_id)
        return render_template("partials/bookmark_item.html", bookmark=bookmark)
    return redirect("/")

@app.route("/bookmark/<int:id>/edit-form")
def edit_form(id):
    bookmark = get_bookmark(id)
    if not bookmark:
        return "Bookmark not found", 404
    folders = get_all_folders()
    tags = get_all_tags()
    return render_template("partials/edit_modal.html",
        bookmark=bookmark,
        folders=folders,
        tags=tags
    )

@app.route("/bookmark/<int:id>/update", methods=["POST"])
def update_bookmark_route(id):
    title = request.form.get("title", "")
    folders = [f.strip() for f in request.form.get("folders", "").split(",") if f.strip()]
    tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]

    update_bookmark(id, {
        "title": title,
        "folders": folders,
        "tags": tags,
    })

    if is_htmx():
        bookmark = get_bookmark(id)
        response = make_response(
            render_template("partials/bookmark_item.html", bookmark=bookmark)
        )
        response.headers["HX-Trigger"] = "closeModal"
        return response

    return redirect(request.referrer or "/")

@app.route("/bookmark/<int:id>/favorite", methods=["POST"])
def toggle_favorite_route(id):
    toggle_favorite(id)
    if is_htmx():
        bookmark = get_bookmark(id)
        view = request.form.get("view", "list")
        if view == "grid":
            return render_template("partials/bookmark_card.html", bookmark=bookmark)
        return render_template("partials/bookmark_item.html", bookmark=bookmark)
    return redirect(request.referrer or "/")

@app.route("/bookmark/<int:id>/archive", methods=["POST"])
def toggle_archive_route(id):
    toggle_archive(id)
    if is_htmx():
        return ""
    return redirect(request.referrer or "/")

@app.route("/bookmark/<int:id>/delete", methods=["POST"])
def delete_bookmark_route(id):
    delete_bookmark(id)
    if is_htmx():
        return ""
    return redirect("/")

@app.route("/folder/<name>")
def folder_view(name):
    bookmarks = get_bookmarks(folder=name)
    folders = get_all_folders()
    tags = get_all_tags()
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        active_filter=name
    )

@app.route("/folders", methods=["POST"])
def add_folder():
    name = request.form.get("name", "").strip()
    if not name:
        return "", 400
    create_folder(name)
    if is_htmx():
        folders = get_all_folders()
        return render_template("partials/folder_list.html", folders=folders)
    return redirect("/")

@app.route("/tag/<name>")
def tag_view(name):
    bookmarks = get_bookmarks(tag=name)
    folders = get_all_folders()
    tags = get_all_tags()
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        active_filter=name
    )

@app.route("/favorites")
def favorites():
    bookmarks = get_favorites()
    folders = get_all_folders()
    tags = get_all_tags()
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        active_filter="Favorites"
    )

@app.route("/archived")
def archived():
    bookmarks = get_archived()
    folders = get_all_folders()
    tags = get_all_tags()
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        active_filter="Archived"
    )

@app.route("/untagged")
def untagged():
    bookmarks = get_untagged()
    folders = get_all_folders()
    tags = get_all_tags()
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        active_filter="Untagged"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")