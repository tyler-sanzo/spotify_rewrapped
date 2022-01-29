
from flask import Flask, render_template, request, redirect, session, url_for

# python modules for data manipulation and visualization
import pandas as pd
import mpld3
import seaborn as sns
import matplotlib

# this fixes the problem with threading in matplotlib
matplotlib.use('Agg')

# spotify api authorization and call handling library
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# local python files
from keys import client_id, client_secret

port = 5000


def top_tracks_cleaner(data):
	x = []
	s = data['items']

	for i in s:
		x.append({
        	'song': i['name'],
            'album': i['album']['name'],
            'artists': [artist['name'] for artist in i['artists']],
            'id': i['id'],
            'popularity': i['popularity'],
            'img': i['album']['images'][0]['url']
            })
	
	return x

<<<<<<< HEAD
=======
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
>>>>>>> 97458212a3636c2928280712d9757c62f19b573c

app = Flask(__name__)
app.secret_key = 'wowza'


auth_manager = SpotifyOAuth(
	scope=['user-top-read',
	'user-read-recently-played',
	'user-library-read'
	],
	client_id=client_id,
	client_secret=client_secret,
	redirect_uri=f"http://127.0.0.1:{port}",
	show_dialog=True
	)


# home route. renders index.html 
@app.route('/', methods=['GET', 'POST'])
def home():

	# executes if api sends a get request with the 'code' argument
	if request.args.get('code'):
		
		# this saves the auth token into a session object
		session['access_token'] = request.args.get('code')

		return redirect('/user_data')

	# initial load in template this renders essentially only renders on the first load
	return render_template('index.html')

@app.route('/user_data')
def user_data():
	

	auth_manager.get_access_token(session.get('access_token'))
	sp = spotipy.Spotify(auth_manager=auth_manager)


	if not request.args.get('time_range'):
		return redirect('/user_data?time_range=short_term')


	# return your top features and a matplot viz
	if request.args.get('time_range'):

		# api call to get top songs in some range, clean and set as df
		time_range = request.args['time_range']

		# calling for the user data and simultaneously cleaning/framing
		df = pd.DataFrame(
			top_tracks_cleaner(
				sp.current_user_top_tracks(limit=50, time_range=time_range)))


<<<<<<< HEAD
		# saving IDs for future calls
		id_list = df['id'].to_list()
=======
			# api call to get top artists in some range, clean and set as df
			artists_json = sp.current_user_top_artists(limit=data['num_tracks'], time_range=data['time_range'])
			top_artists_df = pd.DataFrame(top_artists_cleaner(artists_json))
			top_artists_df.index += 1

			# api call to grab the features of those songs from their IDs
			id_list = top_tracks_df['id'].to_list()
			features_json = sp.audio_features(id_list)
			features_df = pd.DataFrame(features_json)
>>>>>>> 97458212a3636c2928280712d9757c62f19b573c

		# api call to grab the features of those songs from their IDs
		features_json = sp.audio_features(id_list)
		features_df = pd.DataFrame(features_json)

		# merge the two df on their ID
		merged = pd.merge(df, features_df).drop(labels=['uri', 'track_href', 'analysis_url', 'duration_ms'], axis=1)


		# plotting each feature / saving the svg in a dictionary
		sns.set_style('dark')
		sns.set_context("paper")

		histogram_svg_elements = {}
		histogrammable_features = ['popularity', 'key', 'loudness', 'tempo']

		for feature in histogrammable_features:
			song_feature_series = merged[feature]


			fig = sns.displot(data=song_feature_series, kde=True, height=4, aspect=1).set(ylabel=None, xlabel=None).fig


			# using mpld3 library to save as an html svg
			histogram_svg_elements[feature] = mpld3.fig_to_html(fig)
			matplotlib.pyplot.clf()


		features = merged[['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']]



		return render_template('user_data.html', plots=histogram_svg_elements, data=merged)

	# if neither condition is met
	return '<a href="/">Home</a>'

<<<<<<< HEAD
=======
			
			# this gets top 10 artists assets for sean
			top_ten_artists = []
			for i in range(10):
				d = {
				'artist': artists_json['items'][i]['name'],
				'genres': artists_json['items'][i]['genres'],
				'artist_art': artists_json['items'][i]['images'][0]['url']
				}
				top_ten_artists.append(d)
			

			return render_template('user_data.html', data=top_ten, data2=top_ten_artists, summary=plot_html)
>>>>>>> 97458212a3636c2928280712d9757c62f19b573c


# this route is essentially only the middleman so the page doesnt save
@app.route('/login', methods=['POST'])
def login_function():

	auth_url = auth_manager.get_authorize_url()
	return redirect(auth_url)



if __name__ == '__main__':
	app.run(debug=True, port=port)