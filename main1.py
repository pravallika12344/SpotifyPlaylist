import datetime as dt
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import config

# Number of years to go back, make sure there was a Billboard chart published
YEARS_AGO = 20
PAGE_URL = "https://www.billboard.com/charts/hot-100/"
# The scope required by the Spotify API, to allow the creation and modification of playlists
SCOPE = "playlist-modify-private"
# Instead of some fake website address, just using localhost for this
REDIRECT_URL = "http://localhost:8888/callback"


def get_date():
    """Returns the date in the past as a string, going back the defined amount of years."""
    today = dt.datetime.now().date()
    past_date = today - dt.timedelta(days=YEARS_AGO * 365)
    return past_date.strftime("%Y-%m-%d")


def load_site(past_date):
    """Takes a date as a string and scrapes the defined site, returns songs and artists as lists."""
    page_url = PAGE_URL + past_date
    response = requests.get(url=page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    song_names_spans = soup.select("li ul li h3")
    artist_name = soup.findAll(name="span", class_="a-no-trucate")
    song_names = []
    artists = []
    for i in song_names_spans:
        song_names.append(i.getText().strip())
    for i in artist_name:
        artists.append(i.getText().split('\n')[2].split('\t')[1])
    print(artists)
    return song_names, artists


# Calculate the date in the past
date = get_date()
# Get lists of songs and artists for that year
song_list, artist_list = load_site(date)

# Authorize through spotipy
oauth = SpotifyOAuth(
    scope=SCOPE,
    redirect_uri=REDIRECT_URL,
    client_id="4aacf381aaa54222ac594fa4ac087ebf",
    client_secret="1d3a6e88a389453f95afa119540bbf30",
    show_dialog=True,
    cache_path="token.txt"
)
sp = spotipy.Spotify(auth_manager=oauth)

song_uris = []
for i in range(len(song_list)):
    result = sp.search(
        q=f"track:{song_list[i]} year:{date.split('-')[0]} artist:{artist_list[i]}",
        type="track",
        limit=1
    )
    print(result)
    if result["tracks"]["items"]:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)

# Get the user ID
user_id = sp.current_user()["id"]
# Create the playlist
playlist = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",
    public=False
)
# Add the songs
# sp.playlist_add_items(playlist["id"], song_uris)

if "id" in playlist:
    playlist_id = playlist["id"]
    print("Playlist created successfully. ID:", playlist_id)

    # Add the songs
    sp.playlist_add_items(playlist_id, song_uris)
    print("Songs added to the playlist.")
else:
    print("Failed to create the playlist.")
