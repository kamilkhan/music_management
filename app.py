from flask import render_template,Flask,request,redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid

app = Flask(__name__, static_folder='static')


@app.route('/home')
def home():
    conn = sqlite3.connect('music')
    cursor = conn.execute("SELECT album,title,artist,uuid from songs")
    items = make_items(cursor)
    conn.close()
    return render_template('home.html', items=items,no_of_songs=len(items))


@app.route('/search', methods=['POST'])
def search():
    search_token = request.form.get('search')
    if search_token == '':
        return redirect("/home", code=302)
    conn = sqlite3.connect('music')
    query = "select album,title,artist,uuid from songs where album like '%" + search_token \
            + "%' or title like '%" + search_token + "%' or artist like '%" + search_token + "%'"
    cursor = conn.execute(query)
    items = make_items(cursor)
    conn.close()
    return render_template('home.html', items=items, search_text=search_token, no_of_songs=len(items))


@app.route("/")
def root():
    return redirect("/home", code=302)


@app.route('/upload_song_form')
def upload_form():
    return render_template('upload_song_form.html')


@app.route('/upload_song', methods=['POST'])
def upload():
    if request.method == 'POST':
        d = request.files
        album = request.form.get('album')
        title = request.form.get('title')
        artist = request.form.get('artist')
        f = d.get('filename')
        fname = f.filename
        if album == '' and title == '' and artist == "":
            return render_template("upload_song_form.html", error_message="Please enter either album or title or artist")
        if fname == '':
            return render_template("upload_song_form.html", error_message = "Please select Audio File")
        uuid_string = str(uuid.uuid1())
        fname = uuid_string + ".mp3"
        if not os.path.isdir(os.getcwd() + "/static/songs"):
            os.makedirs(os.getcwd() + "/static/songs")
        f.save(os.getcwd() + "/static/songs/"+fname)
        conn = sqlite3.connect('music')
        cur = conn.cursor()
        cur.execute("INSERT INTO songs (uuid,album,title,artist) values (?,?,?,?)", (uuid_string, album, title, artist))
        conn.commit()
        conn.close()
    return redirect("/home", code=302)


@app.route("/delete/<string:uuid>", methods=["POST"])
def delete(uuid):
    conn = sqlite3.connect('music')
    cur = conn.cursor()
    cur.execute("DELETE from songs where uuid = '" + uuid + "'")
    conn.commit()
    conn.close()
    os.remove("static/songs/" + uuid + ".mp3")
    return redirect("/home", code=302)


@app.route('/download/<path:uuid>', methods=['GET'])
def download(uuid):
    filename = uuid + ".mp3"
    return send_from_directory(directory='static/songs', path=filename, as_attachment=True)


@app.route('/play/<path:uuid>', methods=['GET'])
def play(uuid):
    filename = uuid + ".mp3"
    return render_template('play_song.html', filename=filename)


@app.route('/play_shared_song/<string:uuid>', methods=['GET'])
def play_shared_song(uuid):
    filename = uuid + ".mp3"
    return render_template('play_shared_song.html',filename=filename)


@app.route('/share/<string:uuid>', methods=['GET'])
def share(uuid):
    port = "5000"
    ip_address = "localhost"
    url = "http://"+ip_address+":"+port+"/play_shared_song/" + uuid
    return render_template('share_page.html', url=url)


def make_items(cursor):
    items = []
    for row in cursor:
        item = dict()
        item['album'] = row[0]
        item['title'] = row[1]
        item['artist'] = row[2]
        item['uuid'] = row[3]
        items.append(item)
    return items


