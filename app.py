from flask import render_template,Flask,request,redirect, send_from_directory
from werkzeug.utils import secure_filename
import db
import os
import uuid


def create_app():
    music_app = Flask(__name__, instance_relative_config=True)
    music_app.config.from_mapping(
        # need to change secret key in production
        SECRET_KEY='dev', DATABASE=os.path.join(music_app.instance_path, 'music'),
    )
    music_app.config['folder'] = '/static/'
    try:
        os.makedirs(music_app.instance_path)
    except OSError:
        pass
    db.init_app(music_app)
    return music_app


app = create_app()


@app.route('/home')
def home():
    conn = db.get_db()
    cursor = conn.execute("SELECT album,title,artist,uuid from songs")
    items = make_items(cursor)
    return render_template('home.html', items=items,no_of_songs=len(items))


@app.route('/search', methods=['POST'])
def search():
    search_token = request.form.get('search')
    if search_token == '':
        return redirect("/home", code=302)
    conn = db.get_db()
    query = "select album,title,artist,uuid from songs where album like '%" + search_token \
            + "%' or title like '%" + search_token + "%' or artist like '%" + search_token + "%'"
    cursor = conn.execute(query)
    items = make_items(cursor)
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
        file_name = f.filename
        if album == '' and title == '' and artist == "":
            return render_template("upload_song_form.html", error_message="Please enter either album or title or artist")
        if file_name == '':
            return render_template("upload_song_form.html", error_message = "Please select Audio File")
        uuid_string = str(uuid.uuid1())
        file_name = uuid_string + ".mp3"
        f.save(os.getcwd() + app.config['folder'] + file_name)
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO songs (uuid,album,title,artist) values (?,?,?,?)", (uuid_string, album, title, artist))
        conn.commit()
    return redirect("/home", code=302)


@app.route("/delete/<string:uuid>", methods=["POST"])
def delete(uuid):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("DELETE from songs where uuid = '" + uuid + "'")
    conn.commit()
    os.remove(os.getcwd() + "/static/" + uuid + ".mp3")
    return redirect("/home", code=302)


@app.route('/download/<path:uuid>', methods=['GET'])
def download(uuid):
    filename = uuid + ".mp3"
    return send_from_directory(directory='static', path=filename, as_attachment=True)


@app.route('/play/<path:uuid>', methods=['GET'])
def play(uuid):
    filename = uuid + ".mp3"
    conn = db.get_db()
    query = "select album,title,artist from songs where uuid = '" + uuid + "'"
    row = conn.execute(query).fetchone()
    return render_template('play_song.html', filename=filename, album=row[0], title=row[1], artist=row[2])


@app.route('/play_shared_song/<string:uuid>', methods=['GET'])
def play_shared_song(uuid):
    filename = uuid + ".mp3"
    conn = db.get_db()
    query = "select album,title,artist from songs where uuid = '" + uuid + "'"
    row = conn.execute(query).fetchone()
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


