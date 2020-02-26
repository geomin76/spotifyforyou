from flask import Flask
from os import abort
import sys

from flask import render_template, request, redirect, session, url_for
from six.moves.urllib.parse import quote
import json
from service.spotify_service import *
from secrets import *


app = Flask(__name__)


CLIENT_ID = client_id()
CLIENT_SECRET = client_secret()

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

# CLIENT_SIDE_URL = "https://playlist-statistics-267218.appspot.com/"
# REDIRECT_URI = 'https://playlist-statistics-267218.appspot.com/callback'
CLIENT_SIDE_URL = "http://spotifyforyou.com"
REDIRECT_URI = 'http://spotifyforyou.com/callback'

#for testing locally
# CLIENT_SIDE_URL='http://127.0.0.1:5000'
# REDIRECT_URI = 'http://127.0.0.1:5000/callback'

SCOPE = "user-library-read user-read-currently-playing playlist-read-collaborative user-library-modify playlist-read-private playlist-modify-public playlist-modify-private user-top-read"
app.secret_key = secret_key()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

#directs to introduction page
@app.route('/')
def main():
    return render_template('intro.html')



@app.route("/authorize")
def authorize():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

#after getting user access token, it redirects to home page
@app.route('/callback')
def callback():
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    response_data = json.loads(post_request.text)
    session['tokens'] = {
        'access_token': response_data["access_token"],
        'refresh_token': response_data["refresh_token"]
    }
    return redirect(url_for('index'))


@app.route('/index')
def index():
    if 'tokens' not in session:
        abort(400)
    sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    data = user_content(sp)
    playlists = playlist(sp)
    return render_template('index.html', data=data, playlists=playlists)


@app.route('/playlist_intro')
def playlist_intro():
    sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    playlists = playlist(sp)
    return render_template('playlist_intro.html', playlists=playlists)


#clean this method
@app.route('/playlist_select', methods=['GET', 'POST'])
def playlist_select():
    select = request.form.get('comp_select')
    sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    stats = playlist_calculation(sp, select)
    return render_template("playlist_select.html", playlist=select, stats=stats)


@app.route("/recs")
def recs():
    sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    genres = []
    for gen in sp.recommendation_genre_seeds()['genres']:
        genres.append(gen)
    return render_template("recs.html", genre=genres)


@app.route("/recs_final", methods=['GET', 'POST'])
def recs_final():
    specs = {
        'name': request.form['name'],
        'number': request.form['quantity'],
        'select': request.form.get('comp_select'),
        'dance': request.form['danceability'],
        'valence': request.form['valence'],
        'energy': request.form['valence']
    }
    name = recs_playlist(session['tokens'].get('access_token'), specs=specs)
    return render_template("recs_final.html", name=name)


@app.route("/top_stats_intro")
def top_stats_intro():
    return render_template("top_stats_intro.html")


@app.route("/top_stats", methods=['GET', 'POST'])
def top_stats():
    limit = request.form['limit']
    time = request.form['time']
    top = get_top(session['tokens'].get('access_token'), limit, time)
    return render_template("top_stats.html", stats=top)


#use the search function and get a artist related to an artist, give top 10 songs and have it in a box


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)