import os
from flask import Flask, render_template, Response, request, redirect
from audio_recording import audio_stream as aud
from utils import flask_utils as u
from time import time

# Startup Code
app = Flask(__name__)
for f in ['active_recordings', 'raw_audio']:
    u.make_folder_if_not_exist(f)
#
#
@app.route("/", methods=["GET"])
def serve_homepage():
    """
    Renders index page
    """
    return render_template('index.html')


@app.route("/get_available_wakewords", methods=["GET"])
def get_available_wakewords():
    """
    Gets available wakewords (for populating wakeword dropdown)
    """
    return {'wakewords': [''] + u.get_available_wakewords()}


@app.route("/create_wakeword", methods=["GET"])
def create_wakeword():
    """
    Renders page for creating a new wakeword
    """
    return render_template('set_wakeword.html')


@app.route("/accept_wakeword/<wakeword_name>", methods=["POST"])
def accept_wakeword(wakeword_name):
    """
    Accepts new wakeword sample
    """
    wakeword_name = wakeword_name.replace(' ', '_')
    aud.save_new_wakeword(request.data, wakeword_name)
    return {"response": "accepted"}


@app.route("/use_wakeword", methods=["GET"])
def recorder():
    """
    Renders Use Wakeword page
    """
    return render_template('use_wakeword.html')


@app.route("/audio_reciever/<wakeword_name>/<ts>", methods=["POST"])
def audio_reciever(wakeword_name, ts):
    """
    Endpoint for detecting wakeword in audio stream
    """

    result = aud.ingest_blob_from_js(request.data, f'{ts}.wav')

    return {'result': result}


if __name__ == "__main__":

    import socket

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    # app.run(ssl_context='adhoc')
    # app.run(host=local_ip, port=8088, debug=True, ssl_context='adhoc')
    app.run(host='0.0.0.0', port=8088, debug=True, ssl_context="adhoc")
