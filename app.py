from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("base.html",
        folders=["Design", "Tech", "Running"],
        tags=["Read Later", "Programming", "FOSS Software"]
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")