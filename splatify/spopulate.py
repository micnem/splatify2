from django.shortcuts import render, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests import Request, post
from .models import Artist, TopArtist, RelatedArtist, Profile
import requests as r
import json


BASE_URL = "https://api.spotify.com/v1/"

def execute_spotify_api_request(access_token, endpoint, post_=False, put_=False):
    
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + access_token}

    if post_:
        r.post(BASE_URL + endpoint, headers=headers)
    if put_:
        r.put(BASE_URL + endpoint, headers=headers)

    response = r.get(BASE_URL + endpoint, {}, headers=headers)
    try:
        return response.json()
    except:
        return {'Error': 'Issue with request'}

def create_artist(items):
    artist_list = []
  
    for item in items:
        spotify_id = item.get('id')
        # image = item.get('images')[0].get('url')
        name = item.get('name')
        popularity = item.get('popularity')
        uri = item.get('uri')

        artist = {
            'spotify_id': spotify_id,
            'name': name,
            # 'image': image,
            'popularity': popularity,
            'uri': uri
        }

        artist_list.append(artist)
    
    return artist_list


def get_top_artists(profile):
    access_token = profile.account.social_auth.first().extra_data['access_token']
    endpoint = "me/top/artists?time_range=medium_term&limit=30"
    response = execute_spotify_api_request(access_token, endpoint)

    if response == None:
        endpoint = "me/top/artists?time_range=short_term&limit=30"
        response = execute_spotify_api_request(access_token, endpoint)

    items = response.get('items')
    artist_list = create_artist(items)

    for num, artist in enumerate(artist_list[::-1]):
        current_artist, created = Artist.objects.get_or_create(name = artist['name'], spotify_id = artist['spotify_id'], popularity = artist['popularity'], uri = artist['uri'])
        print(current_artist.spotify_id)
        endpoint = f"artists/{current_artist.spotify_id}/related-artists"
        print(BASE_URL + endpoint)
        response = execute_spotify_api_request(access_token, endpoint)
        print(response)
        items = response.get('artists')

        rel_artist_list = create_artist(items)
    

        for number, rel_artist in enumerate(rel_artist_list[::-1]):
            related_artist, created = Artist.objects.get_or_create(name = rel_artist['name'], spotify_id = rel_artist['spotify_id'], popularity = rel_artist['popularity'], uri = rel_artist['uri'])
            RelatedArtist.objects.get_or_create(root_artist=current_artist, artist2=related_artist, affinity=number + 1)


        ta, created = TopArtist.objects.get_or_create(artist=current_artist, profile=profile, affinity=num+1)
        
    profile.populated = True
    profile.save()
    


def match(user_list):
    master_artist_list = []
    for num, user in enumerate(user_list):
        top_artists = user.profile.fave_artists.all()
        related_artists = RelatedArtist.objects.filter(root_artist__in = top_artists).distinct().values_list("artist2", flat=True)
        artist_list = (Artist.objects.filter(id__in = related_artists)|top_artists).distinct()
        if num == 0:
            master_artist_list = artist_list
        else:
            master_artist_list = master_artist_list.intersection(artist_list)

    print(master_artist_list)

    return master_artist_list
    

def create_playlist(profile, user2):
    access_token = profile.account.social_auth.last().extra_data['access_token']
    user_id = profile.account.social_auth.first().uid
    endpoint = f"users/{user_id}/playlists"
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + access_token}
    body = json.dumps({
          "name": f"SplatList for {profile.account.username} and {user2.username}",
          "description": "A playlist generated for you, by Splatify, with love.",
          "public": False
        })
    response = r.post(BASE_URL + endpoint, body, headers=headers)
    playlist_id = response.json()
    return playlist_id['id']

    

def add_to_playlist(profile, track_id_list, playlist_id):
    access_token = profile.account.social_auth.first().extra_data['access_token']
    playlist_id = playlist_id
    track_urls = '%2c'.join(track_id_list)
    endpoint = f"playlists/{playlist_id}/tracks?uris=" + track_urls
    response = execute_spotify_api_request(access_token, endpoint, post_=True)
    return response
   

def get_artist_top_songs(artist, profile):
    access_token = profile.account.social_auth.first().extra_data['access_token']
    artist_id = artist.spotify_id
    endpoint = f"artists/{artist_id}/top-tracks?country=IL"
    response = execute_spotify_api_request(access_token, endpoint)
    print(f"Showing top songs for {artist.name}")

    tracks = response['tracks']
    track_id_list = []
    for track in tracks:
        track_id_list.append(track['uri'])
    
    return track_id_list

 

def main(master_artist_list, profile, user2):
    master_artist_list = master_artist_list[0:20]
    playlist_id = create_playlist(profile, user2)
    for artist in master_artist_list:
        add_to_playlist(profile, get_artist_top_songs(artist, profile), playlist_id)
    return playlist_id
    print("SPLATTED")


# track_list = ['spotify:track:522S15x223yj5B4yeDoGUN', 'spotify:track:4xcWHWVVj7FgETLICCSqpk', 'spotify:track:2bD8h96DIELpgzUfLsGERH', 'spotify:track:3qRFJHRJWV2f3JINS6tLvU', 'spotify:track:1vFhGIUnOTZMiJtWzg9hhK', 'spotify:track:6f5NqVOtXZieSyjrDX0fLE', 'spotify:track:79XLBlqbbTxqZeRuzUr5Lg', 'spotify:track:0VlJd8EekBe5AXfFOAvBNI', 'spotify:track:4fm43n2lgmqzQras001xnF', 'spotify:track:159L5lOCpzANKrZpSK8TLZ']
