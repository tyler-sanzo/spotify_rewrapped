from flask import Flask, render_template, request, redirect, session, url_for

import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from keys import client_id, client_secret

"""
def saved_songs_cleaner(data):    
    x = []
    s = data['items']

    for i in s:
        x.append({
            'added_at': i['added_at'],
            'song': i['track']['name'],
            'album': i['track']['album']['name'],
            'artists': i['track']['artists'][0]['name'],
            'id': i['track']['id'],
            'popularity': i['track']['popularity']
            })

    return x
"""

def top_tracks_cleaner(data):
	x = []
	s = data['items']

	for i in s:
		x.append({
        	'song': i['name'],
            'album': i['album']['name'],
            'artists': i['artists'][0]['name'],
            'id': i['id'],
            'popularity': i['popularity']
            })
	
	return x


def top_artists_cleaner(data):
	x = []
	s = data['items']

	for i in s:
		x.append({
        	'artist': i['name'],
            'genres': i['genres'],
            'id': i['id'],
            'popularity': i['popularity']
            })
	
	return x


app = Flask(__name__)
app.secret_key = 'wowza'


auth_manager = SpotifyOAuth(
	scope=['user-top-read',
	'user-read-recently-played',
	'user-library-read',
	'user-library-read'
	],
	client_id=client_id,
	client_secret=client_secret,
	redirect_uri="http://localhost:8888/",
	show_dialog=True
	)


# home route. renders index.html 
@app.route('/', methods=['GET', 'POST'])
def home():

	# executes if api sends a get request with the 'code' argument
	if request.args.get('code'):
		
		# this saves the auth token into a session object
		session['access_token'] = request.args.get('code')

		return render_template('logged_in.html')

	
	# block executes if a post is sent
	# here is where api calls are executed
	if request.method == 'POST':

		auth_manager.get_access_token(session.get('access_token'))
		sp = spotipy.Spotify(auth_manager=auth_manager)

		"""
		# executes if a post is sent with form data key 'saved_tracks'
		if request.form.get('saved_tracks'):
			
			saved_tracks = sp.current_user_saved_tracks(limit=50, offset=0)
			df = pd.DataFrame(saved_songs_cleaner(saved_tracks))

			return render_template('user_data.html', data=df.to_html())
		"""			

		# if a post with form data key= 'top_tracks'
		if request.form.get('top_tracks'):
			data = request.form			
			top_tracks = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
			df = pd.DataFrame(top_tracks_cleaner(top_tracks))
			df.index += 1

			return render_template('user_data.html', data=df.to_html())

		# return your top features
		if request.form.get('top_features'):

			data = request.form
			tracks_json = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
			artists_json = sp.current_user_top_artists(limit=data['num_tracks'], time_range=data['time_range'])
			top_tracks_df = pd.DataFrame(top_tracks_cleaner(tracks_json))
			top_artists_df = pd.DataFrame(top_artists_cleaner(artists_json))
			top_artists_df.index += 1

			id_list = top_tracks_df ['id'].to_list()
			features_json = sp.audio_features(id_list)
			features_df = pd.DataFrame(features_json)

			merged = pd.merge(top_tracks_df, features_df).drop(labels=['uri', 'track_href', 'analysis_url', 'duration_ms'], axis=1)
			merged.index += 1
			summary = merged.describe()

			return render_template('user_data.html', data2=top_artists_df.to_html(), data=merged.to_html(), summary=summary.to_html())
			#return render_template('user_data.html', data=top_artists_df.to_html(), summary=summary.to_html())

	# initial load in template this renders essentially only renders on the first load
	return render_template('index.html')


# this route is essentially only the middleman so the page doesnt save
@app.route('/login', methods=['POST'])
def login_function():

	auth_url = auth_manager.get_authorize_url()
	return redirect(auth_url)



if __name__ == '__main__':
	app.run(debug=True, port=8888)