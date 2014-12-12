from scraper import WTTSParser
from scraper import SpotifyEditor
from oauth2 import Oauth2


def test():
	CLIENT_ID = "your_id_here"
	CLIENT_SECRET = "your_secret_here"
	POSTBACK_URI = "http://127.0.0.1:8000"
	STATE = "test"
	PLAYLIST_PERMISSION = "playlist-read-private playlist-modify-public playlist-modify-private"

	parser = WTTSParser()
	parser.parseArtistSongList()
	records = parser.getRecords()
	
	#begin authentication
	oauth2 = Oauth2(CLIENT_ID, CLIENT_SECRET, PLAYLIST_PERMISSION, STATE)
	token = oauth2.get_token()
	token = oauth2.obtain_authorization(token)

	sp = SpotifyEditor(token)
	
	playlist = "WTTS Overeasy"
	#sp.create_playlist(playlist)
	sp.add_records_to_playlist(records, playlist)

if __name__ == "__main__":
	test()