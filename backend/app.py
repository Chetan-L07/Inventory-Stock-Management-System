from flask import Flask


app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Chetan_Loves_Nagu🐍</h1>"


if __name__ == "__main__":
    app.run(debug = True)