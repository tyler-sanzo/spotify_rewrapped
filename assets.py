def song_table(data: list):
	
	ordered_list = []


	for index, d in enumerate(data):
		ordered_list.append(
			f'''

			<li>
				<div class='list_item'>
					
					<div class='song_info'>
						<div class='song_name'>
							<span><b>{d['song']}</b><span>
						</div>
						<div class='artist_name'>
							<span>{', '.join(d['artist'])}<span>
						</div>
						<div class='album_name'>
							<span>{d['album']}</span>
						</div>
					</div>

					<img src={d['img']} alt='number {index + 1} song: {d['song']}' class='album_art' style="width: 10rem; height: 10rem;">

				</div>
			</li>

			'''
			)

	return "<ol class=top_tracks_list>" + ''.join(ordered_list) + "</ol>"