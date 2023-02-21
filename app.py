from flask import render_template,Flask,request, redirect
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)


@app.route('/home')
def home():
    conn = sqlite3.connect('music')
    items = list()
    cursor = conn.execute("SELECT album,title,artist,file_name from songs")
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


@app.route('/upload_song_form')
def upload_form():
    return render_template('upload_song_form.html')


@app.route('/upload_song', methods=['POST'])
def upload():
    if request.method == 'POST':
        d = request.files
        #print("EE" + d.get('filename'))
        if d.get("filename") is None:
            return render_template("error_page.html", an_optional_message="Error uploading file")
        album= request.form.get('album')
        title = request.form.get('title')
        artist = request.form.get('artist')
        f = d.get('filename')
        fname = f.filename
        f.save(fname)
        print(album, title, artist, fname)
        conn = sqlite3.connect('music')
        cur = conn.cursor()
        cur.execute("INSERT INTO songs (album,title,artist,file_name) values (?,?,?,?)",
                     (album, title, artist, fname))
        #cur.execute("INSERT INTO s (a) values (?)", album)
        conn.commit()
        conn.close()
    return redirect("/home", code=302)