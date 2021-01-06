from django.shortcuts import render
from .spopulate import get_top_artists, create_playlist, match, main
from .models import *

def check_profile(profile):
    if not profile.populated:
        get_top_artists(profile)

        
def homepage(request):
    return render(request, 'homepage.html')


def room(request):
    check_profile(request.user.profile)

    users = User.objects.all()
    
    return render(request, 'room.html', {'users': users})

def show_top_artists(request):
    return render(request,'top_artists.html')

def splat(request, user_id):
    user2 = User.objects.get(id=user_id)
    master_list = match([request.user, user2])
    playlist_id = main(master_list, request.user.profile, user2)

    return render(request, 'result.html', {'playlist_id':playlist_id})

def play(request, playlist_id):
    
    return render(request, 'play.html', {'playlist_id':playlist_id})