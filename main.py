# -*- coding: utf-8 -*-
"""
ASOT Playlist Updater
This script will update the given playlist from the authorized user with the latest Armin van Buuren ASOT Radio episode
The script requires the following environment variables to be set:
    CLIENT_ID: The client ID of the Spotify app
    CLIENT_SECRET: The client secret of the Spotify app
    REFRESH_TOKEN: The refresh token of the authorized user
    PLAYLIST_ID: The ID of the playlist to update
    USER_ID: The ID of the authorized user
The script requires the following packages to be installed:
    requests
"""

class AppAuthorization():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._auth_token = None
        self._headers = None

    @property
    def auth_token(self):
        import requests
        if self._auth_token is None:
            url = 'https://accounts.spotify.com/api/token'
            auth_response = requests.post(url, {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            })
            self._auth_token = auth_response.json()['access_token']
        return self._auth_token

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
        return self._headers

class UserAuthorization():
    def __init__(self, user_id, app, refresh_token):
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.app = app
        self._auth_token = None
        self._headers = None

    @property
    def auth_token(self):
        import requests
        if self._auth_token is None:
            url = 'https://accounts.spotify.com/api/token'
            payload=f'grant_type=refresh_token&refresh_token={self.refresh_token}&client_id={self.app.client_id}&client_secret={self.app.client_secret}'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                }
            response = requests.request("POST", url, headers=headers, data=payload)
            self._auth_token = response.json()['access_token']
        return self._auth_token

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
        return self._headers

def get_most_recent_album(app, base_url, artist_id):
    import requests
    # Get most recent album
    recent_album = requests.get(f'{base_url}/artists/{artist_id}/albums', headers=app.headers, params={
        'include_groups': 'album',
        'limit': 1,
        'market': 'US'
    })
    return recent_album.json()['items'][0]['id'], recent_album.json()['items'][0]['name'], recent_album.json()['items'][0]['total_tracks']

def get_album_tracks(app, base_url, album_id):
    import requests
    album_endpoint = requests.get(f'{base_url}/albums/{album_id}/tracks?limit=20&offset=0', headers=app.headers)
    album_tracks = []
    while True:
            tracks = album_endpoint.json()['items']
            for track in tracks:
                album_tracks.append(track['uri'])
            if album_endpoint.json()['next'] is not None:
                album_endpoint = requests.get(album_endpoint.json()['next'], headers=app.headers)
            else:
                break
    return album_tracks

def empty_playlist(user, base_url, playlist_id):
    import requests
    while True:
        track_ids = []
        playlist_endpoint = requests.get(f'{base_url}/playlists/{playlist_id}/tracks?limit=50&offset=0', headers=user.headers)
        if playlist_endpoint.json()['items']:
            tracks = playlist_endpoint.json()['items']
            for track in tracks:
                track_ids.append({'uri':track['track']['uri']})
                requests.delete(f'{base_url}/playlists/{playlist_id}/tracks', headers=user.headers, json={
                'tracks': track_ids
            })
        else:
            break

def update_playlist(user, base_url, new_tracks, latest_name, PLAYLIST_ID):
    import requests
    import sys

    # Update the name of the playlist
    playlist = requests.put(f'{base_url}/playlists/{PLAYLIST_ID}', headers=user.headers, json={
        'name': f'ASOT Radio - Latest Episode',
        'description': latest_name
    })
    if playlist.status_code == 200:
        sys.stdout.write('# Playlist updated successfully :)\n')
    else:
        sys.stdout.write('# Playlist update failed :(\n')
    # Add new tracks to the playlist
    requests.post(f'{base_url}/playlists/{PLAYLIST_ID}/tracks', headers=user.headers, json={
        'uris': new_tracks
    })

def get_current_playlist(user, base_url, playlist_id):
    import requests
    playlist = requests.get(f'{base_url}/playlists/{playlist_id}', headers=user.headers)
    return playlist.json()['description'], playlist.json()['tracks']['total']


def main():
    import os
    import sys
    from datetime import datetime

    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
    PLAYLIST_ID = os.environ['PLAYLIST_ID']
    USER_ID = os.environ['USER_ID']

    sys.stdout.write(f'--------------------------------------------------------------------------------\n')
    sys.stdout.write(f'Starting script at {datetime.now()}...\n')
    sys.stdout.write(f'--------------------------------------------------------------------------------\n')
    sys.stdout.write('# Getting app authorization...\n')
    app = AppAuthorization(CLIENT_ID, CLIENT_SECRET)
    sys.stdout.write('# Getting user authorization...\n')
    user = UserAuthorization(USER_ID, app, REFRESH_TOKEN)
    # base URL of all Spotify API endpoints
    base_url = 'https://api.spotify.com/v1'
    # artist ID for Armin van Buuren ASOT Radio
    artist_id = '25mFVpuABa9GkGcj9eOPce'
    # get most recent album + tracks
    sys.stdout.write('# Checking current playlist info...\n')
    playlist_desc, playlist_length = get_current_playlist(user, base_url, PLAYLIST_ID)
    sys.stdout.write(f'# > Current playlist:\n')
    sys.stdout.write(f'# \t{playlist_desc}\n')
    sys.stdout.write(f'# \t{playlist_length} tracks\n')
    sys.stdout.write('# Comparing to most recent album...\n')
    latest_id, latest_name, latest_length = get_most_recent_album(app, base_url, artist_id)
    sys.stdout.write(f'# > Most recent album:\n')
    sys.stdout.write(f'# \t{latest_name}\n')
    sys.stdout.write(f'# \t{latest_length} tracks\n')
    if playlist_desc != latest_name or playlist_length != latest_length:
        sys.stdout.write('# > New album detected\n')
        sys.stdout.write('# Getting album tracks...\n')
        album_tracks = get_album_tracks(app, base_url, latest_id)
        sys.stdout.write('# Emptying playlist...\n')
        empty_playlist(user, base_url, PLAYLIST_ID)
        sys.stdout.write('# >>> Updating playlist...\n')
        update_playlist(user, base_url, album_tracks, latest_name, PLAYLIST_ID)
    else:
        sys.stdout.write('# > Playlist already up to date\n')
    sys.stdout.write(f'--------------------------------------------------------------------------------\n')
    sys.stdout.write('Exiting script\n')
    sys.stdout.write(f'--------------------------------------------------------------------------------\n')

if __name__ == '__main__':
    main()
