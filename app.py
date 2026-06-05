import os
from functools import wraps
from flask import Flask, render_template, redirect, request, session
from urllib.parse import urlparse
from db import get_bookmarks, get_bookmark, get_all_folders, get_all_tags, create_bookmark, delete_bookmark, update_bookmark, create_folder, create_tag, toggle_archive, toggle_favorite, get_favorites, get_untagged, get_archived, get_stats
from scraper import fetch_metadata
from files import save_article

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
print("SECRET KEY:", app.secret_key)  # add this line temporarily

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def is_htmx():
    return request.headers.get("HX-Request") == "true"

def sidebar_context():
    return {
        "folders": get_all_folders(),
        "tags": get_all_tags()
    }

@app.route("/login")
def login():
    if session.get("logged_in"):
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    if (username == os.environ.get("KEEPER_USER", "admin") and
            password == os.environ.get("KEEPER_PASSWORD", "password")):
        session["logged_in"] = True
        return redirect("/")
    return render_template("login.html", error="Invalid credentials")


@app.route("/")
@login_required
def index():
    q = request.args.get("q", "")
    bookmarks = get_bookmarks(q=q)
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        stats=stats,
    )

@app.route("/grid")
@login_required
def grid():
    bookmarks = get_bookmarks()
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)
    if is_htmx():
        return render_template("partials/bookmark_grid.html",
            bookmarks=bookmarks
        )
    return render_template("grid.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        stats=stats,
    )

@app.route("/bookmark/<int:id>")
@login_required
def reading(id):
    bookmark = get_bookmark(id)
    if not bookmark:
        return "Bookmark not found", 404
    stats = get_stats([bookmark])    # wrap in a list
    return render_template("reading.html",
        bookmark=bookmark,
        stats=stats,
        **sidebar_context()
    )

@app.route("/bookmark/<int:id>/item")
@login_required
def bookmark_item(id):
    bookmark = get_bookmark(id)
    return render_template("partials/bookmark_item.html", bookmark=bookmark)

@app.route("/bookmarks", methods=["POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def toggle_archive_route(id):
    toggle_archive(id)
    if is_htmx():
        return ""
    return redirect(request.referrer or "/")

@app.route("/bookmark/<int:id>/delete", methods=["POST"])
@login_required
def delete_bookmark_route(id):
    delete_bookmark(id)
    if is_htmx():
        return ""
    return redirect("/")

@app.route("/folder/<name>")
@login_required
def folder_view(name):
    bookmarks = get_bookmarks(folder=name)
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)

    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        stats=stats,
        active_filter=name
    )

@app.route("/folders", methods=["POST"])
@login_required
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
@login_required
def tag_view(name):
    bookmarks = get_bookmarks(tag=name)
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)

    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        stats=stats,
        active_filter=name
    )

@app.route("/tags", methods=["POST"])
@login_required
def add_tag():
    name = request.form.get("name", "").strip()
    if not name:
        return "", 400
    create_tag(name)
    if is_htmx():
        tags = get_all_tags()
        return render_template("partials/tag_list.html", tags=tags)
    return redirect("/")

@app.route("/favorites")
@login_required
def favorites():
    bookmarks = get_favorites()
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        stats=stats,
        active_filter="Favorites"
    )

@app.route("/archived")
@login_required
def archived():
    bookmarks = get_archived()
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)
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
@login_required
def untagged():
    bookmarks = get_untagged()
    folders = get_all_folders()
    tags = get_all_tags()
    stats = get_stats(bookmarks)
    if is_htmx():
        return render_template("partials/bookmark_list.html",
            bookmarks=bookmarks
        )
    return render_template("index.html",
        bookmarks=bookmarks,
        folders=folders,
        tags=tags,
        stats=stats,
        active_filter="Untagged"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")