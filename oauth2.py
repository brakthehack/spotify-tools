import urllib.request
import urllib.parse
from urllib.parse import quote

import webbrowser
import os.path

import http.server
import http.client

import json
import base64
import time

#Python 3 compatible
class Oauth2:
	"""
	Description::
		Client for obtaining spotify access through oauth2.
		This class provides a user-friendly method of authenticating
		by using the browser.  The user has no need to handle access codes manually.
		Token caching is automatically handled by the client

	Usage::
		oauth2 = Oauth2(CLIENT_ID, CLIENT_SECRET, SCOPE, STATE, POSTBACK_URI)
		token = oauth2.get_token()
		token = oauth2.obtain_authorization(token)

	"""

	MAX_NUM_REQUESTS = 5
	CACHE_FILE = "oauth_token.txt"

	def __init__(
		self,
		client_id=None,
		client_secret=None,
		scope=None,
		state=None,
		redirect_uri="http://127.0.0.1:8000",
		response_type="code",
		show_dialog=None):
		self.token_cache = None
		self.server = None
		self.url = ""
		self.baseUrl = "https://accounts.spotify.com/authorize/?"
		self.client_id = client_id
		self.client_secret = client_secret
		self.response_type = response_type
		self.redirect_uri = redirect_uri
		self.state = state
		self.scope = scope
		self.show_dialog = show_dialog
		self._build_url()

	def _build_url(self):
		self.url = self.baseUrl
		self._add_to_url(self.client_id, "client_id", False)
		self._add_to_url(self.response_type, "response_type", False)
		self._add_to_url(quote(self.redirect_uri), "redirect_uri", False)
		self._add_to_url(self.state, "state", True)
		self._add_to_url(quote(self.scope), "scope", True)
		self._add_to_url(self.show_dialog, "show_dialog", True)
		self.url = self.url[:-1]

	def _add_to_url(self, var, varName, optional):
		if var is not None:
			self.url += varName + "=" + var + "&"
		elif optional is False:
			raise Exception(varName + " must be not null.")
		else:
			print("Optional parameter ", varName, " optional and not provided")

	def get_token(self, server="127.0.0.1", port=8000):
		"""
			Waits for a token response from the spotify service
			If a token cache exists already, return the cached token
		"""
		self._load_token_cache()
		# we return none because if we have a VALID cached token,
		# then there is no access token to get
		if self.token_cache is not None:
			return None

		if self.server is None:
			self.server = SpotifyHTTPServer((server, port), SpotHTTPHandler)

		# open the link in the user's default web browser, and redirect to our server
		webbrowser.open(self.url)
		i = 0
		# since an invalid request returns None 
		# we give the user/system a few times to get it right
		while self.server.access_code is None and i < Oauth2.MAX_NUM_REQUESTS:
			self.server.handle_request()
			i += 1
		return self.server.access_code

	def _load_token_cache(self):
		if os.path.isfile(Oauth2.CACHE_FILE):
			cache = open(Oauth2.CACHE_FILE, "r")
			self.token_cache = json.loads(cache.read())
			cache.close()

	def _write_token_to_cache(self, token):
		cache = open(Oauth2.CACHE_FILE, "w")
		token["time_requested"] = time.time()
		cache.write(json.dumps(token))
		cache.close()

	def _remove_token_cache(self):
		os.remove(Oauth2.CACHE_FILE)
		self.token_cache = None

	def _is_valid_token(self):
		"""
			Returns a valid token from the cache if one exists
			If no valid token is found, return None
		"""
		token = self.token_cache 
		if token is None:
			return False

		return token["expires_in"] + token["time_requested"] > \
			time.time()

	def obtain_authorization(self, bearer=None, encoding='utf-8'):
		"""
			Posts the login authentication ticket to the server to receive the access token
			Param: bearer the json object representing an authenticated user
		"""

		url = "https://accounts.spotify.com/api/token"
		request = urllib.request.Request(url)

		params = None
		if bearer is None:
			self._load_token_cache()
			if self._is_valid_token():
				return self.token_cache["access_token"]
			else: # remove old token and provide appropriate params for refresh if applicable
				if "refresh_token" in self.token_cache:
					params = self._make_refresh_body(self.token_cache["refresh_token"], encoding)
					header = self._make_refresh_header(encoding)
					request.add_header(header[0], header[1]) # new auth header
					print(header[0], ' ', header[1])
				else:
					self._remove_token_cache()
					params = self._make_access_body(self.get_token(), encoding)

		else:
			params = self._make_access_body(bearer, encoding)


		request.add_header("Content-Type","application/x-www-form-urlencoded;charset=" + encoding)

		f = urllib.request.urlopen(request, params)

		token = f.read().decode(encoding)
		bearer = json.loads(token)
		self._write_token_to_cache(bearer)
		return bearer["access_token"]

	def _make_access_body(self, token, encoding='utf-8'):
		return urllib.parse.urlencode({
			'grant_type': 'authorization_code',
			'code': token,
			'redirect_uri': self.redirect_uri,
			'client_id': self.client_id,
			'client_secret': self.client_secret })\
		.encode(encoding)

	def _make_refresh_header(self, encoding='utf-8'):
		token = self.client_id + ":" + self.client_secret
		token = token.encode(encoding)
		return 'Authorization', 'Basic ' + base64.b64encode(token).decode(encoding)

	def _make_refresh_body(self, token, encoding='utf-8'):
		return urllib.parse.urlencode({
			'grant_type': 'refresh_token',
			'refresh_token': token }) \
		.encode(encoding)

###############################################################################

class SpotifyHTTPServer(http.server.HTTPServer):

	def __init__(self, binding, handler):
		super().__init__(binding, handler)
		self.access_code = None

###############################################################################

class SpotHTTPHandler(http.server.BaseHTTPRequestHandler):

		def do_HEAD(self):
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

		def do_GET(self):
			response = "<html><head></head><body>Authentication successful.  " + \
			"You may now close this window. <br></body></html>"
			paths = urllib.parse.urlparse(self.path)
			queries = dict(urllib.parse.parse_qsl(paths[4]))
			if 'code' not in queries:
				response = "<html><head></head><body>Error: Authentication failed<br></body></html>"
			else:
				self.server.access_code = queries['code']

			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(response.encode("utf-8"))

###############################################################################