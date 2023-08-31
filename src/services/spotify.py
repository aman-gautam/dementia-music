import requests
import os

def get_top_tracks(artist, country):
    # Set your Spotify API credentials
    # CLIENT_ID = 'your_client_id'
    # CLIENT_SECRET = 'your_client_secret'

    # Base URL for Spotify API
    BASE_URL = 'https://api.spotify.com/v1/'

    # Authenticate and get access token
    auth_response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'client_credentials',
        'client_id': os.environ['SPOTIFYCLIENTID'],
        'client_secret': os.environ['SPOTIFYCLIENTSECRET'],
    })

    auth_data = auth_response.json()
    access_token = auth_data['access_token']

    # Headers for API requests
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Get artist ID by searching for the artist
    artist_name = artist
    search_response = requests.get(BASE_URL + 'search', headers=headers, params={
        'q': '"'+artist_name+'"',
        'type': 'artist',
        'limit': 1
    })
    search_data = search_response.json()

    artist_id = search_data['artists']['items'][0]["id"]

    # Get top tracks of the artist
    top_tracks_response = requests.get(BASE_URL + f'artists/{artist_id}/top-tracks', headers=headers, params={
        'country': country  # Replace with desired country code
    })

    top_tracks_data = top_tracks_response.json()
    top_tracks = top_tracks_data['tracks']
    
    # # Print the 15 most popular songs and their URLs
    # for idx, track in enumerate(top_tracks):
    #     print(f"{idx + 1}. {track['name']} - {track['external_urls']['spotify']} -- {track['preview_url']}")
    return top_tracks