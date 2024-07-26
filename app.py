from flask import Flask, request, jsonify
from shazamio import Shazam
import requests
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

async def recognize_song(file_bytes):
    result = await shazam.recognize_song(file_bytes)
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
    data = request.get_json()
    audio_url = data.get('audio_url', '')

    if not audio_url:
        return jsonify({'error': 'Audio URL is required'}), 400

    try:
        # تحميل الملف الصوتي من URL
        response = requests.get(audio_url)
        response.raise_for_status()  # تأكد من عدم وجود أخطاء في التحميل
        audio_data = response.content

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        song_data = loop.run_until_complete(recognize_song(audio_data))
        return jsonify(song_data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error downloading audio file: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error recognizing song: {str(e)}'}), 500

def run_flask_app():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    run_flask_app()
