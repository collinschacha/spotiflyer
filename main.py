import os
import zipfile

from flask import Flask, session, redirect, url_for,request,render_template,current_app,send_file
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from youtube import youtube_search_cli
from youtube_downloader import startDownload

DOWNLOAD_FOLDER = './downloads'

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

app.config["SECRET_KEY"] = os.urandom(64)


client_id = ""
client_secret = ""
redirect_uri =  "http://127.0.0.1:5000/callback"
scope = "playlist-read-private"


cache_handler = FlaskSessionCacheHandler(session)

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(auth_manager=sp_oauth)


def auth_validator():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)


@app.route("/")
def home():
    return render_template("index.html")    

@app.route("/login")
def login():
    auth_validator()

    return redirect(url_for("get_playlist"))

@app.route("/callback")
def callback():
    sp_oauth.get_access_token(request.args["code"])
    return redirect(url_for("get_playlist"))

@app.route("/get_playlist")
def get_playlist():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    playlists_info = [( pl["images"][0]["url"], pl["name"],pl["id"]) for pl in playlists["items"]]


  
    return render_template("get_playlist.html", playlists_info=playlists_info)

@app.route('/single_playlist/<playlist_id>')
def single_playlist(playlist_id):
    try:
        playlist = sp.playlist(playlist_id=f"{playlist_id}", fields=None, market=None, additional_types=("tracks"))
        playlist_name = playlist['name']
        num_tracks = len(playlist['tracks']['items'])
        track_names = [item['track']['name'] for item in playlist['tracks']['items']]
        print(f"Number of tracks: {num_tracks}")
        print(f"Track names: {track_names}")
        zip_file = zipfile.ZipFile('downloads.zip', 'w')
        ddir = os.path.join(current_app.root_path, app.config['DOWNLOAD_FOLDER'])
        for track in track_names:
            youtube =  youtube_search_cli(track)
            youtube_id = str(youtube)
            file_path = os.path.join(ddir, f"{track}.mp4")
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=f"{track}.mp4")
            else:
                startDownload(youtube_id=youtube_id) 
                if os.path.exists(file_path):
                    zip_file.write(file_path, arcname=f"{track}.mp4")
                    print("Added file to zip")
        zip_file.close()
        return send_file('downloads.zip', as_attachment=True)
    except:
        return "Playlist not found"
    

@app.route("/logout")
def logout():
    cache_handler.clear()
    session.clear
    return redirect(url_for("home"))


        


if __name__ == "__main__":
    app.run(debug=True)