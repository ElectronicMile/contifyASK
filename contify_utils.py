import spotipy
from ask_sdk_core.utils import request_util
from ask_sdk_model.ui import LinkAccountCard

def login(handler_input):
	token = request_util.get_account_linking_access_token(handler_input)
	if not token:
		speech_text = "Unfortunately you have not linked your spotify account. Please check your Alexa app to do so."
		return None, speech_text, True, None

	try:
		sp = spotipy.Spotify(auth=token)
	except spotipy.SpotifyException:
		speech_text = "Your Spotify account is no longer linked successfully. Please check your Alexa app."
		return None, speech_text, True, None

	return token, "", False, sp

def process_context(curr, sp):

	context_is_type = True
	try:
		type = curr["context"]["type"]
		uri = curr["context"]["uri"]
		if not curr["is_playing"]:
			return "Currently paused"
	except TypeError:
		context_is_type = False

	track = curr["item"]["name"]
	artist = curr["item"]["artists"][0]["name"]
	device = curr["device"]["name"]

	if type == "artist":
		contextname = sp.artist(uri)["name"]
	elif type == "album":
		contextname = sp.album(uri)["name"]
	elif type == "playlist":
		pl = uri.split(":")
		contextname = sp.user_playlist(pl[2], pl[4], "name")["name"]

	if context_is_type:
		out = "The context is of type %s: '%s'. Currently the track '%s' by '%s' is playing on %s." % (
			type, contextname, track, artist, device)
	else:
		out = "There is no context, you are listening to your library. Currently the track %s by %s is playing on %s." % (
			type, track, artist, device)

	return out


def get_current_context(sp):
	urlplayer = 'https://api.spotify.com/v1/me/player'
	params = {'country': None, 'album_type': None, 'limit': 20, 'offset': 0}
	payload = None
	curr = sp._internal_call('GET', urlplayer, payload, params)
	if not curr:
		return "Currently not playing anything on Spotify."
	else:
		return process_context(curr, sp)

def authorize(handler_input):
	resp = handler_input.response_builder
	token, speech_text, authproblem, sp = login(handler_input)

	if authproblem:
		resp.set_card(LinkAccountCard())