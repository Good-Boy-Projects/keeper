from flask import Flask, render_template
from db import get_bookmarks, get_bookmark, get_all_folders, get_all_tags

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")