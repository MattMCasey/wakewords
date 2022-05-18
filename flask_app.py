import os
from flask import Flask, render_template, Response, request, redirect
from audio_recording import audio_stream as aud
from utils import flask_utils as u
from time import time


app = Flask(__name__)
#
#
@app.route("/", methods=["GET"])
def serve_homepage():
    return render_template('index.html')


@app.route("/get_available_wakewords", methods=["GET"])
def get_available_wakewords():
    return {'wakewords': [''] + u.get_available_wakewords()}


@app.route("/create_wakeword", methods=["GET"])
def create_wakeword():
    return render_template('set_wakeword.html')


@app.route("/accept_wakeword/<wakeword_name>", methods=["POST"])
def accept_wakeword(wakeword_name):
    aud.save_new_wakeword(request.data, wakeword_name)
    # print('accept_wakeword')
    print(wakeword_name)
    # print(dir(request))
    # print(request.data)
    return {"response": "accepted"}


@app.route("/recorder", methods=["GET", "POST"])
def recorder():
    if request.method == "POST":
        f = request.files['audio_data']
        with open('audio.wav', 'wb') as audio:
            f.save(audio)

        return render_template('recorder.html', request="POST")
    else:
        return render_template('recorder.html')

# @app.route("/recorder2", methods=["GET", "POST"])
# def recorder():
#     if request.method == "POST":
#         f = request.files['audio_data']
#         with open('audio.wav', 'wb') as audio:
#             f.save(audio)
#         print('file uploaded successfully')
#
#         return render_template('recorder2.html', request="POST")
#     else:
#         return render_template('recorder2.html')

# @app.route("/get_filename", methods=["GET"])
# def get_filename():
#     filename = str(round(time())) + '.wav'
#     print(filename)
#     return {'filename': filename}


@app.route("/audio_reciever/<wakeword_name>", methods=["POST"])
def audio_reciever(wakeword_name):
    print(wakeword_name)
    print(request.form)
    # print(dir(request.args.to_dict()))
    # print(request.args.to_dict())
    print(request.content_length)
    # print(request.get_data())
    # print(request.get_json())
    # ts = str(round(time()))
    ts = 'test'
    result = aud.save_blob_from_js(request.data, f'{ts}.wav')

    return {'result': result}
    # # print(request.data)
    # return 'autio_reciever pinged'

# @app.route("/a2", methods=["GET"])
# def root():
#     return render_template('index.html')

@app.route("/access_stream", methods=["GET"])
def get_stream():
    aud.accept_stream()
    render_template("<h1>We're listening</h2>")

#
#
# @app.route('/save-record', methods=['POST'])
# def save_record():
#     # check if the post request has the file part
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(request.url)
#     file = request.files['file']
#     print(dir(request.files))
#     print(request.files.keys())
#     # if user does not select file, browser also
#     # submit an empty part without filename
#     if file.filename == '':
#         flash('No selected file')
#         return redirect(request.url)
#     file_name = str(uuid.uuid4()) + ".mp3"
#     full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
#     file.save(full_file_name)
#     return '<h1>Success</h1>'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8088, debug=True)
