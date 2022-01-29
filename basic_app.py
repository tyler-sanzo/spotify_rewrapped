
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
from assets import song_table

port = 5000

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

# def density_to_html(df, metrics=None):

# 	# this just allows you to specify columns in the df
# 	# ax is the plot object
# 	if metrics:
# 		ax = df[metrics].plot.density()
# 	else:
# 		# plot will use these columns to measure if you dont specify
# 		# trying to future proof this by limitting to ints and floats inclusively between 0 and 1
# 		metrics = [i for i in df.columns if (df[i].dtype in ['int64', 'float64']) and (0 <= df[i].mean() <= 1)]
# 		ax = df[metrics].plot.density()
		
# 	# use .get_figure() to produce the figure element for mpld3
# 	fig = ax.get_figure()
# 	html = mpld3.fig_to_html(fig)

# 	return html

app = Flask(__name__)
app.secret_key = 'wowza'


auth_manager = SpotifyOAuth(
	scope=['user-top-read',
	'user-read-recently-played',
	'user-library-read'
	],
	client_id=client_id,
	client_secret=client_secret,
	redirect_uri=f"http://localhost:{port}/",
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




		# # executes if a post is sent with form data key 'saved_tracks'
		# if request.form.get('saved_tracks'):
			
		# 	saved_tracks = sp.current_user_saved_tracks(limit=50, offset=0)
		# 	df = pd.DataFrame(saved_songs_cleaner(saved_tracks))

		# 	return render_template('user_data.html', data=df.to_html())

		# # if a post with form data key= 'top_tracks'
		# if request.form.get('top_tracks'):
		# 	data = request.form			
		# 	top_tracks = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
		# 	df = pd.DataFrame(top_tracks_cleaner(top_tracks))
		# 	df.index += 1

		# 	return render_template('user_data.html', data=df.to_html())




		# return your top features and a matplot viz
		if request.form.get('top_features'):

			# api call to get top songs in some range, clean and set as df
			data = request.form



			top_short_json = sp.current_user_top_tracks(limit=50, time_range='short_term')
			top_mid_json = sp.current_user_top_tracks(limit=50, time_range='medium_term')
			top_long_json = sp.current_user_top_tracks(limit=50, time_range='long_term')


			top_short_df = pd.DataFrame(top_tracks_cleaner(top_short_json))
			top_mid_df = pd.DataFrame(top_tracks_cleaner(top_mid_json))
			top_long_df = pd.DataFrame(top_tracks_cleaner(top_long_json))


			df = top_short_df.copy()	# TODO: change later when we figure out how to decide which to use


			# api call to grab the features of those songs from their IDs
			id_list = df['id'].to_list()
			features_json = sp.audio_features(id_list)
			features_df = pd.DataFrame(features_json)

			# merge the two df on their ID
			merged = pd.merge(df, features_df).drop(labels=['uri', 'track_href', 'analysis_url', 'duration_ms'], axis=1)
			# merged.index += 1

			

			'''# plot will use these columns to measure if you dont specify
												# trying to future proof this by limitting to ints and floats inclusively between 0 and 1
												df = merged.copy()
												metrics = [i for i in df.columns if (
													(df[i].dtype in ['int64', 'float64']) and
													(0 <= df[i].mean() <= 1))]
												
												ax = df[metrics].plot.density()
												
												# use .get_figure() to produce the figure element for mpld3
												fig = ax.get_figure()
												features_density_html = mpld3.fig_to_html(fig)'''



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




			# # takes key info from top_tracks call to pass to webpage
			# top_ten = []
			# for i in range(10):
			# 	top_ten.append({
			# 	'img': tracks_json['items'][i]['album']['images'][0]['url'],
			# 	'album': tracks_json['items'][i]['album']['name'],
			# 	'artist': [artist['name'] for artist in tracks_json['items'][i]['artists']],
			# 	'song': tracks_json['items'][i]['name']
			# 	})

			return render_template('user_data.html',
				plots=histogram_svg_elements,
				data=merged
				)

	# initial load in template this renders essentially only renders on the first load
	return render_template('index.html')

# this route is essentially only the middleman so the page doesnt save
@app.route('/login', methods=['POST'])
def login_function():

	auth_url = auth_manager.get_authorize_url()
	return redirect(auth_url)



if __name__ == '__main__':
	app.run(debug=True, port=port)