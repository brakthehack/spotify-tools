# -*- coding: utf-8 -*-

from htmldom import htmldom
import html
import json

import spotipy
from oauth2 import Oauth2

import time
from functools import reduce

############################################################################

class SpotifyEditor:
	"""
		Editor that performs functions on an authenticated spotify user's library
	"""
	MAX_SEARCH_HITS = 2

	def __init__(self, token=None):
		self.sp = spotipy.Spotify(auth=token)
		print(token)
		me = self.sp.me()
		self.id = me["id"]

	def create_playlist(self, name, public=True):
		self.sp.user_playlist_create(self.id, name, public)

	def get_playlist_id_by_name(self, name):
		playlists = self.sp.user_playlists(self.id)["items"]
		for playlist in playlists:
			if playlist["name"] == name:
				return playlist["id"]
		return None

	def add_records_to_playlist(self, records, playlist):
		"""
			Adds a collection of records to a given playlist
			records: a collection of key value pairs Record(artist, song)
			playlist: a playlist name
		"""
		pId = self.get_playlist_id_by_name(playlist)
		if pId is None:
			return
		ids = []
		for record in records:
			recordId = self._get_record_by_name(record)
			if recordId is not None:
				print("Found record: ", 
				record.song, " by ", record.artist, 
				" to playlist ", playlist)
				ids.append(recordId)
		self.add_uniques_to_playlist(pId, ids)

	def add_uniques_to_playlist(self, playlistId, ids):
		"""
			Given a list of track identifiers, add a list of track ids 
			to a playlist pid that do not already exist in the playlist
		"""
		existing = set()
		newItems = set(ids)
		pl = self.sp.user_playlist(self.id, playlistId)
		paging = pl["tracks"]
		while True:
			for track in paging["items"]:
				existing.add(track["track"]["id"])
			paging = self.sp.next(paging)
			if paging is None:
				break

		toAdd = newItems - existing
		if len(toAdd) < 1:
			print("No new items added to playlist")
		else:
			self.sp.user_playlist_add_tracks(self.id, playlistId, toAdd)



	
	def _get_record_by_name(self, record):
		"""
			searches for a record using the api, gets the match, and returns
			the uri of the record to be looked up
		"""
		print("Getting: ", record.song, ", ", record.artist)
		result = self.sp.search("artist:" + record.artist + 
								" title:" + record.song, 
								SpotifyEditor.MAX_SEARCH_HITS, 0, "track")
		items = result["tracks"]["items"]
		if len(items) < 1:
			print("Could not find ", record.song, " by ", record.artist)
			return None
		else:
			return items[0]["id"]

############################################################################

class WTTSParser:

	def __init__(self, url='http://wttsfm.com/on-air/overeasy/'):
		self.dom = self.createDom(url)
		self.records = []

	def createDom(self, url):
		return htmldom.HtmlDom(url).createDom()

	def parseArtistSongList(self):
		"""
			Fills the list of records 
			Subclasses should override this method
		"""
		p = self.dom.find("h4").next()

		sunking = "(Sun King Studio 92)"
		slen = len(sunking) * -1

		for node in p:
			text = self._unescape(node.text()).split("\n")
			i = 0
			artist = None
			for line in text:
				line = line.strip()
				if len(line) > 1:
					if i % 2 == 0:
						artist = line
					else:
						if line.endswith(sunking):
							line = line[:slen]
						self.records.append(Record(artist, line))
					i += 1

	def getRecords(self):
		return self.records

	def _unescape(self, text):
		"""
			Simple unescaper for HTML
		"""
		repls ={"&lt;": "<", 
				"&gt;": ">", 
				"&amp;": "&", 
				"&#8220;": "", 
				"&#8221;": "", 
				"&#8217;": "\'"}
		return reduce(lambda a, kv: a.replace(*kv), repls.items(), text)

############################################################################

class Record:
	def __init__(self, artist, song):
		self.artist = artist
		self.song = song