from flask import Flask, request, jsonify
from shazamio import Shazam
import asyncio

app = Flask(__name__)
shazam = Shazam()

async def search_track(query, limit):
    result = await shazam.search_track(query=query)
    tracks = result.get('tracks', {}).get('hits', [])
    return tracks[:limit]

async def search_artist(query, limit):
    result = await shazam.search_artist(query=query)
    artists = result.get('artists', {}).get('hits', [])
    return artists[:limit]

async def recognize(file_bytes):
    result = await shazam.recognize(file_bytes)
    return result

@app.route('/search/track', methods=['POST'])
def search_track_route():
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 10)

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    try:
        limit = int(limit)
    except ValueError:
        return jsonify({'error': 'Invalid limit value'}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tracks = loop.run_until_complete(search_track(query, limit))
    
    return jsonify(tracks)

@app.route('/search/artist', methods=['POST'])
def search_artist_route():
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 10)

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    try:
        limit = int(limit)
    except ValueError:
        return jsonify({'error': 'Invalid limit value'}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    artists = loop.run_until_complete(search_artist(query, limit))
    
    return jsonify(artists)

@app.route('/recognize-song', methods=['POST'])
def recognize_song_route():
    audio_data = request.files.get('audio')
    if not audio_data:
        return jsonify({'error': 'Audio file is required'}), 400
    try:
        result = asyncio.run(recognize(audio_data))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Error recognizing song: {str(e)}'}), 500

def run_flask_app():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    run_flask_app()
