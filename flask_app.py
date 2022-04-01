import os
from flask import Flask, render_template, Response, request, redirect
from audio_recording import audio_stream as aud


app = Flask(__name__)
#
#
# @app.route("/recorder", methods=["GET", "POST"])
# def recorder():
#     if request.method == "POST":
#         f = request.files['audio_data']
#         with open('audio.wav', 'wb') as audio:
#             f.save(audio)
#         print('file uploaded successfully')
#
#         return render_template('recorder.html', request="POST")
#     else:
#         return render_template('recorder.html')
#
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
    app.run(debug=True)
