from flask import Flask, request, jsonify, send_file
from pytube import YouTube, Search
from pydub import AudioSegment
import os
import tempfile

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_videos():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        search = Search(query)
        results = search.results
        videos = [{"title": video.title, "url": video.watch_url} for video in results]
        return jsonify({"videos": videos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Télécharger la vidéo YouTube
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()

        # Créer un fichier temporaire pour la vidéo
        temp_video = tempfile.NamedTemporaryFile(delete=False)
        video.download(filename=temp_video.name)

        # Conversion en MP3
        temp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        audio = AudioSegment.from_file(temp_video.name)
        audio.export(temp_mp3.name, format="mp3")

        # Supprimer le fichier vidéo temporaire
        os.remove(temp_video.name)

        # Retourner le fichier MP3 pour téléchargement
        return send_file(temp_mp3.name, as_attachment=True, download_name=f"{yt.title}.mp3")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
