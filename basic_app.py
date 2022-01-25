
from flask import Flask, render_template, request, redirect, session, url_for

import pandas as pd

import mpld3
import matplotlib
matplotlib.use('Agg')

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from keys import client_id, client_secret


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

def density_to_html(df, metrics=None):

	# this just allows you to specify columns in the df
	# ax is the plot object
	if metrics:
		ax = df[metrics].plot.density()
	else:
		# plot will use these columns to measure if you dont specify
		# trying to future proof this by limitting to ints and floats inclusively between 0 and 1
		metrics = [i for i in df.columns if (df[i].dtype in ['int64', 'float64']) and (0 <= df[i].mean() <= 1)]
		ax = df[metrics].plot.density()
		
	# use .get_figure() to produce the figure element for mpld3
	fig = ax.get_figure()
	html = mpld3.fig_to_html(fig)

	return html

app = Flask(__name__)
app.secret_key = 'wowza'


auth_manager = SpotifyOAuth(
	scope=['user-top-read',
	'user-read-recently-played',
	'user-library-read'
	],
	client_id=client_id,
	client_secret=client_secret,
	redirect_uri="http://127.0.0.1:5000",
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

		# if a post with form data key= 'top_tracks'
		if request.form.get('top_tracks'):
			data = request.form			
			top_tracks = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
			df = pd.DataFrame(top_tracks_cleaner(top_tracks))
			df.index += 1

			return render_template('user_data.html', data=df.to_html())

		# return your top features and a matplot viz
		if request.form.get('top_features'):

			# api call to get top songs in some range, clean and set as df
			data = request.form
			tracks_json = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
			top_tracks_df = pd.DataFrame(top_tracks_cleaner(tracks_json))

			# api call to get top artists in some range, clean and set as df
			artists_json = sp.current_user_top_artists(limit=data['num_tracks'], time_range=data['time_range'])
			top_artists_df = pd.DataFrame(top_artists_cleaner(artists_json))
			top_artists_df.index += 1

			# api call to grab the features of those songs from their IDs
			id_list = top_tracks_df ['id'].to_list()
			features_json = sp.audio_features(id_list)
			features_df = pd.DataFrame(features_json)

			# merge the two df on their ID
			merged = pd.merge(top_tracks_df, features_df).drop(labels=['uri', 'track_href', 'analysis_url', 'duration_ms'], axis=1)
			merged.index += 1

			# simple pandas summary of the data
			summary = merged.describe()

			# making an html plot object with my function
			plot_html = density_to_html(merged)


			return render_template('user_data.html', data2=top_artists_df.to_html(), data=merged.to_html(), summary=plot_html)

	# initial load in template this renders essentially only renders on the first load
	return render_template('index.html')

# this route is essentially only the middleman so the page doesnt save
@app.route('/login', methods=['POST'])
def login_function():

	auth_url = auth_manager.get_authorize_url()
	return redirect(auth_url)



if __name__ == '__main__':
	app.run(debug=True, port=5000)