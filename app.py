from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)


@app.route('/home')
def home():
    conn = sqlite3.connect('music')
    items = list()
    cursor = conn.execute("SELECT album,title,artist, uuid from songs")
    for row in cursor:
        item = dict()
        item['album'] = row[0]
        item['title'] = row[1]
        item['artist'] = row[2]
        items.append(item)
    conn.close()
    return render_template('home.html',items=items)


@app.route("/")
def root():
    return "<p>Welcome to Music Management, Sharing and Streaming Application</p>"
