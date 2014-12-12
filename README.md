spotify-tools
=============

Spotify tools is a set of tools that provide oauth2 support
and automated playlist generation.  The idea is that a user can take a
collection of key-value pairs generated either by a webscraper or some other
method and add them automatically to a playlist.

###Dependencies

* Python 3.x+
* [Spotipy](https://github.com/plamere/spotipy), a lightweight python library for spotify.

Install spotipy by running:
    pip install spotipy

* A spotify app registration.  You can do so [here](https://developer.spotify.com/my-applications/#!/applications)  It takes just a few minutes to register.
* [Requests](https://github.com/kennethreitz/requests) (required by spotipy)

###Quick Start

Use the `test.py` file for a quick demonstration.  In this file, I parse radio
station's website, WTTS Overeasy, who lists a collection of great songs 
each week, and turn it into a spotify playlist.

1. First plug into the `client_id` and `secret_key` you created earlier
into the correct fields inside the test file.
2. uncomment the line `sp.create_playlist(playlist)` if you wish to create
a playlist or change the playlist name to one of your choosing.
3. run `python test.py` You will be prompted to log into your account.
4. The songs will automatically be added to your playlist and you will see
the results displayed on the console.

###License
This software is licensed under the apache commons 2.0 license.
