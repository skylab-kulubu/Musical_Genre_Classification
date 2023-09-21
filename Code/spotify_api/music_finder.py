import base64
import requests
import time
import os


def create_fake_db(client_id, client_secret, callback_url, access_token, token_type, expires_in, refresh_token, scope):
    # Get the timestamp
    timestamp = int(time.time())

    # Refresh token
    access_token, expires_in = refresh_access_token(client_id, client_secret, refresh_token)

    fields = ["client_id", "client_secret", "callback_url", "access_token", "token_type", "expires_in", "refresh_token", "scope", "timestamp"]
    # Create fake_db.txt file 
    with open("fake_db.txt", "w", newline="") as f:
        yazici = csv.DictWriter(f, fieldnames=fields)
        liste = [client_id, client_secret, callback_url, access_token, token_type, expires_in, refresh_token, scope, timestamp]
        yazici.writeheader()
        veri_dict = dict(zip(fields, liste))
        yazici.writerow(veri_dict)

def get_access_token():
    fields = ["client_id", "client_secret", "callback_url", "access_token", "token_type", "expires_in", "refresh_token", "scope", "timestamp"]
    with open("fake_db.txt", "r+", newline="") as f:
        okuyucu = csv.DictReader(f)
        for row in okuyucu:
            # Check if token is expired
            if int(time.time()) - int(row['timestamp']) > int(row['expires_in']):
                # Refresh token
                access_token, expires_in = refresh_access_token(row['client_id'], row['client_secret'], row['refresh_token'])
                row['access_token'] = access_token
                row['expires_in'] = expires_in
                row['timestamp'] = int(time.time())
                yazici = csv.DictWriter(f, fieldnames=fields)
                f.seek(0)
                f.truncate()
                yazici.writeheader()
                yazici.writerow(row)
            return row['access_token']

# Get metadata from spotify
def get_metadata_spotify(spotify_id):
    url = "https://api.spotify.com/v1/tracks/" + spotify_id
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    response = requests.get(url, headers=auth_header)

    author_genres = []
    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    
    for artist in response['artists']:
        for genre in artist.get('genres', []):
            author_genres.append(genre)

    return author_genres
    
# CEZA İD 28Qbi9jTj2eej21P2mImZI
def get_artist_data_spotify(spotify_id):
    url = "https://api.spotify.com/v1/artists/" + spotify_id
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    response = requests.get(url, headers=auth_header)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    return response.json()

def get_spotify_data_from_yt_video_title(yt_video_title):
    url = "https://api.spotify.com/v1/search"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    params = {
        "q": yt_video_title,
        "type": "track",
        "limit": 1
    }
    response = requests.get(url, headers=auth_header, params=params)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    spotify_id = response['tracks']['items'][0]['id']
    author_name = response['tracks']['items'][0]['artists'][0]['name']
    author_id = response['tracks']['items'][0]['artists'][0]['id']
    track_name = response['tracks']['items'][0]['name']
    track_id = response['tracks']['items'][0]['id']
    popularity = response['tracks']['items'][0]['popularity']
    release_date = response['tracks']['items'][0]['album']['release_date']
    duration_s = response['tracks']['items'][0]['duration_ms'] / 1000

    return spotify_id, author_name, author_id, track_name, track_id, popularity, release_date, duration_s

def get_artist_genres_spotify(spotify_id) -> list:
    json_data = get_artist_data_spotify(spotify_id)

    if json_data == 0:
        return 0
    
    genres = []
    
    for genre in json_data.get('genres', []):
        genres.append(genre)

    return genres

def spotify_find_tracks_by_genre(genre, market="TR"):
    url = "https://api.spotify.com/v1/search"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    params = {
        "q": "genre:" + genre,
        "type": "track",
        "limit": 50,
        "market": market
    }
    response = requests.get(url, headers=auth_header, params=params)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    tracks = response['tracks']['items']

    for track in tracks:
        genre = get_artist_genres_spotify(track['artists'][0]['id'])
        print(track['name'], genre, track['artists'][0]['name'], track['popularity'], track['id'], track['album']['release_date'], track['duration_ms'] / 1000, sep="\n-> ")

    return tracks

def refresh_access_token(client_id, client_secret, refresh_token):
    url = "https://accounts.spotify.com/api/token"
    auth_header = {"Authorization": "Basic " + base64.b64encode((client_id + ":" + client_secret).encode()).decode()}

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, headers=auth_header, data=data)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    token = response['access_token']
    expires_in = response['expires_in']
    return token, expires_in        

class Req:
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://www.yt-download.org/"

        # Get the session Cookie and set it
        r = self.session.get(self.url)

        # Parse the Set-Cookie with urllib3
        for cookie in r.cookies:
            name = cookie.name
            value = cookie.value

            print("Setting {}: {}".format(name, value))
            self.update_cookie(name, value)

    def update_cookie(self, name, value):
        self.session.cookies.set(name, value)

    def get(self, url, headers):
        url = self.url + url
        r = self.session.get(url, headers=headers)
        
        # Parse the Set-Cookie with urllib3
        for cookie in r.cookies:
            name = cookie.name
            value = cookie.value

            print("Setting {}: {}".format(name, value))
            self.update_cookie(name, value)

        return r

    def post(self, url, data=None, json=None, headers = None):
        url = self.url + url
        r = self.session.post(url, headers=headers, data=data, json=json)
    
        # Parse the Set-Cookie with urllib3
        for cookie in r.cookies:
            name = cookie.name
            value = cookie.value

            print("Setting {}: {}".format(name, value))
            self.update_cookie(name, value)

        return r

    def get_cookies(self):
        r = self.session.get(self.url)
        return r.cookies

import subprocess
def downlaod_from_yt(yt_video_id):
    # Get the title of the video
    r = requests.get("https://www.youtube.com/watch?v=" + yt_video_id)

    # Get the title of the video    
    title = r.text.split("<title>")[1].split("</title>")[0].replace(" - YouTube", "")

    print("Downloading...")
    # subprocess.Popen(["./win-x64/DownloadYouTube.exe", "-l", yt_video_id])

    return title

def get_tracks_from_playlist(playlist_id):
    url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    response = requests.get(url, headers=auth_header)

    if response.status_code != 200:
        raise Exception("Error (get_tracks_from_playlist) : " + str(response.status_code) + " " + response.text)
    
    tracks = []
    response = response.json()
    track_count = response['total']
    x = 100
    for track in response['items']:
        if track['is_local']:
            continue
        tracks.append(track['track'])
    while x < track_count:
        params = {
            "offset": x
        }
        response = requests.get(url, headers=auth_header, params=params)
        if response.status_code != 200:
            raise Exception("Error (get_tracks_from_playlist) : " + str(response.status_code) + " " + response.text)
        response = response.json()
        for track in response['items']:
            if track['is_local']:
                continue
            tracks.append(track['track'])
        x += 100

    return tracks

def get_author_id_by_name(artist_name):
    # Get author id from spotify by name
    url = "https://api.spotify.com/v1/search"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    response = requests.get(url, headers=auth_header, params=params)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    author_id = response['artists']['items'][0]['id']

    return author_id

def get_top_tracks_by_author_id(author_id):
    url = "https://api.spotify.com/v1/artists/" + author_id + "/top-tracks"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    params = {
        "country": "TR"
    }
    response = requests.get(url, headers=auth_header, params=params)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    tracks = response['tracks']

    return tracks

def get_top_tracks_by_author_name(author_name):
    author_id = get_author_id_by_name(author_name)
    tracks = get_top_tracks_by_author_id(author_id)
    return tracks

def get_tracks_by_author_id(author_id, count = 50):
    url = "https://api.spotify.com/v1/search"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    params = {
        "q": "artist:" + author_id,
        "type": "track",
        "limit": 50
    }
    response = requests.get(url, headers=auth_header, params=params)

    if response.status_code != 200:
        print ("Error: " + str(response.status_code))
        return 0
    
    response = response.json()
    tracks = response['tracks']['items']
    print(tracks)
    return tracks

def get_tracks_by_author_name(author_name, count = 50):
    url = "https://api.spotify.com/v1/search"
    auth_header = {"Authorization": "Bearer " + get_access_token()}
    author_id = get_author_id_by_name(author_name)
    x = 0
    tracks = []
    while x < count:
        limit = 50 if count - x > 50 else count - x
        params = {
            "q": "artist:" + author_name,
            "type": "track",
            "limit": limit,
            "offset": x
        }
        response = requests.get(url, headers=auth_header, params=params)

        if response.status_code != 200:
            raise Exception("Error (get_tracks_by_author_name) : " + str(response.status_code) + " " + response.text)

        response = response.json()
        for track in response['tracks']['items']:
            print(track['artists'][0]['id'], author_id)
            if track['artists'][0]['id'] != author_id:
                print("Not the same author!!!!!")
                continue
            tracks.append(track)
        x += 50
        # NOT: düşük bir olasıkıla son page'de 50 sonuç varsa sorun çıkabilir
        if len(response['tracks']['items']) < 50:
            break
        if len(response['tracks']['items']) == 0:
            break
    return tracks

import numpy as np
def write_to_csv(
        yt_video_name,
        yt_video_id,
        spotify_artist_name,
        spotify_artist_id,
        spotify_artist_genres,
        spotify_track_name,
        spotify_track_id,
        spotify_track_popularity,
        spotify_track_release_date,
        spotify_track_duration_s):
    
    print(
        yt_video_name,
        yt_video_id,
        spotify_artist_name,
        spotify_artist_id,
        spotify_artist_genres,
        spotify_track_name,
        spotify_track_id,
        spotify_track_popularity,
        spotify_track_release_date,
        spotify_track_duration_s,
        sep = "\n-> "
    )
    
    # Write to csv with numpy
    data = np.array([
        yt_video_name,
        yt_video_id,
        spotify_artist_name,
        spotify_artist_id,
        spotify_artist_genres,
        spotify_track_name,
        spotify_track_id,
        spotify_track_popularity,
        spotify_track_release_date,
        spotify_track_duration_s
    ])

    np.savetxt("data.csv", data, delimiter=",", fmt='%s')


def find_yt_video_id_from_name(yt_video_name):
    url = "https://www.youtube.com/results?search_query=" + yt_video_name.replace(" ", "+")
    r = requests.get(url)
    html = r.text

    yt_video_id = html.split("watch?v=")[1].split("\"")[0][:11]
    return yt_video_id

def get_data_by_name(name):
    yt_video_id = find_yt_video_id_from_name(name)
    title = downlaod_from_yt(yt_video_id)
    spotify_id, spotify_artist_name, spotify_artist_id, spotify_track_name, spotify_track_id, spotify_track_popularity, spotify_track_release_date, spotify_track_duration_s = get_spotify_data_from_yt_video_title(name)

    spotify_artist_genres = get_artist_genres_spotify(spotify_artist_id)

    write_to_csv(
        yt_video_name = title,
        yt_video_id = yt_video_id,
        spotify_artist_name = spotify_artist_name,
        spotify_artist_id = spotify_artist_id,
        spotify_artist_genres = spotify_artist_genres,
        spotify_track_name = spotify_track_name,
        spotify_track_id = spotify_track_id,
        spotify_track_popularity = spotify_track_popularity,
        spotify_track_release_date = spotify_track_release_date,
        spotify_track_duration_s = spotify_track_duration_s
    )

# get_data_by_name("ceza med cezir")

def download_preview(preview_url, out_name):
    r = requests.get(preview_url, allow_redirects=True)
    # Create folder and file if not exists
    os.makedirs(os.path.dirname(out_name), exist_ok=True)
    with open(out_name, "wb") as f:
        f.write(r.content)

import csv
def save_tracks_to_cvs(name, tracks):
    with open(name, "w", newline="", encoding='utf-8') as f:
        fields = ["artist_name", "track_name", "track_id", "popularity", "genres", "preview_url"]
        yazici = csv.DictWriter(f, fieldnames=fields)
        yazici.writeheader()
        for track in tracks:
            spotify_artist_genres = get_artist_genres_spotify(track['artists'][0]['id'])
            # open tracks.csv and append
            liste = [track['artists'][0]['name'], track['name'], track['id'], track['popularity'], str(spotify_artist_genres), track['preview_url']]
            veri_dict = dict(zip(fields, liste))
            yazici.writerow(veri_dict)
            # print(track['artists'][0]['name'], track['name'], track['id'], track['popularity'], str(spotify_artist_genres), track['preview_url'], sep=",", file=f)
    print("DONE")

# tracks = spotify_find_tracks_by_genre("rock", "US")

# save_tracks_to_cvs(tracks)
"""
import re
with open("tracks.csv", mode="r", newline="") as f:
    okuyucu = csv.DictReader(f)

    for row in okuyucu:
        if row['preview_url'] == "":
            continue
        url = row['preview_url']
        name = re.sub(r'[\\/*?:"<>|]', '', row['track_name'])
        name = f"previews/{name}-({row['track_id']}).mp3".replace(" ", "_")
        # Check if file exists
        try:
            with open(name, "r"):
                print("File exists" + name)
                continue
        except:
            pass
        print(row['artist_name'], row['track_name'], row['track_id'], row['popularity'], row['genres'], row['preview_url'], sep="\n-> ")
        print(url)
        print(name)
        download_preview(url, name)
"""

import re
def download_preview_from_csv(filename_csv, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(filename_csv, mode="r", newline="", encoding='utf-8') as f:
        okuyucu = csv.DictReader(f)

        for row in okuyucu:
            if row['preview_url'] == "":
                print("No preview url for", row['track_name'])
                continue
            url = row['preview_url']
            name = re.sub(r'[\\/*?:"<>|]', '', row['track_name'])
            name = f"{output_dir}/{name}-({row['track_id']}).mp3".replace(" ", "_")

            # print(row['artist_name'], row['track_name'], row['track_id'], row['popularity'], row['genres'], row['preview_url'], sep="\n-> ")
            # print(url)
            # print(name)
            print(f"Downlaoding {name} from {row['artist_name']}...")
            download_preview(url, name)

# tracks = spotify_find_tracks_by_genre("us_pop", "US")

# save_tracks_to_cvs("us_pop.csv", tracks)

# download_preview_from_csv("us_pop.csv", "us_pop")

# tracks = get_top_tracks_by_author_name("ceza")

# save_tracks_to_cvs("ceza.csv", tracks)

# şimdilik en iyi fonksiyon bu.
tracks = get_tracks_by_author_name("ceza", 70)

save_tracks_to_cvs("ceza.csv", tracks)

download_preview_from_csv("ceza.csv", "ceza")

tracks = get_tracks_from_playlist("0f1H6LMucBQifwSLNU9tFP")

save_tracks_to_cvs("local.csv", tracks)