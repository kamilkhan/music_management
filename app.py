from flask import Flask

app = Flask(__name__)

@app.route("/")
def root():
    return "<p>Welcome to Music Management, Sharing and Streaming Application</p>"
