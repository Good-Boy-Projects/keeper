from flask import Flask, render_template
from db import get_bookmarks, get_all_folders, get_all_tags

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")