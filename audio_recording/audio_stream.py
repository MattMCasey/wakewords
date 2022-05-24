import wave
import os
from audio_recording import model_dummy as model
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.utils import make_chunks
import utils.flask_utils as u
import time
import io
import keras.backend as K


for f in ['active_recordings', 'raw_audio', 'models']:
    u.make_folder_if_not_exist(f)

model_names = ['final_confidence_model.hdf5', 'final_features_model.hdf5']
local_dir = 'models'
s3_prefix = 'model'

for model_name in model_names:
    model.download_latest_model(model_name, local_dir, s3_prefix)

fake_veccer = model.load_model(local_dir, model_names[1])
fake_comparison = model.load_model(local_dir, model_names[0])
model_suite = model.ModelWrapper(fake_veccer, fake_comparison)


RATE = 48000

def save_new_wakeword(blob, filename):
    """
    Ingests new wakeword, breaks it into individual instances. Saves locally.

    :param blob: data stream chunk from web page
    :param filename: str, the name of the folder to put the chunks in

    :returns: None
    """
    s = io.BytesIO(blob)
    audio = AudioSegment.from_file(s, sample_width=2, frame_rate=RATE, format='wav',
                                channels=2)

    folder = f'raw_audio/{filename}/'

    if not os.path.isdir(folder):
        os.mkdir(folder)

    chunks = split_on_silence(audio, min_silence_len = 500,
                              silence_thresh = -40)

    paths = []
    for i, c in enumerate(chunks[:-1]):
        path = os.path.join(folder, str(i) + '.wav')
        paths.append(path)
        c.export(path, format='wav')

    model_suite.generate_new_mean_vector(filename.split('.')[0])


def get_available_wakewords():
    """
    """
    return model_suite.furnish_wakewords()


def get_blob_rolling_window(blob, filename, folder):
    """
    Handles rolling window of audio combining buffer with saved file

    :param blob: data stream chunk from web page
    :param filename: str, the name of the final file

    :returns: output_audio, the windowed audio chunk
    """
    s = io.BytesIO(blob)
    audio = AudioSegment.from_file(s, sample_width=2, frame_rate=RATE,
                                   format='wav', channels=2)

    fpath = f'{folder}/{filename}'

    if os.path.exists(filename):
        existing_audio = AudioSegment.from_file(fpath, sample_width=2,
                                                frame_rate=RATE, format='wav',
                                                channels=2)
        new_audio = existing_audio + audio

    else:
        new_audio = AudioSegment.silent(duration=100000) + audio

    chunks = make_chunks(new_audio, 100)
    output_audio = AudioSegment.silent(duration=0)
    for c in chunks[-20:]:
        output_audio += c

    output_audio.export(fpath, format='wav')

    return output_audio


def purge_old_files(folder, max_mins):
    """
    Purges window files that are more than max_mins old

    :param folder: str, the target folder
    :param max_mins: int, the max number of minutes to leave a file idle

    :returs: None
    """
    target_files = [f'{folder}/{f}' for f in os.listdir(folder) if '.wav' in f]
    file_mtimes = [os.path.getmtime(f) for f in target_files]
    ctime = time.time()
    file_ages = [ctime - t for t in file_mtimes]

    for f, age in zip(target_files, file_ages):
        if age > 60 * max_mins:
            os.remove(f)


def ingest_blob_from_js(blob, filename, target_wakeword):
    """
    Ingests audio. Gets window. Passes to model. Returns result. Cleans up.

    :param blob: data stream chunk from web page
    :param filename: str, the name of the final file

    :returns: model output
    """
    # for some reason, the audio doesn't save right without double-saving it?
    # so I'm also purging audio from the main folder
    folder = 'active_recordings'
    purge_old_files(folder, 5)
    purge_old_files('./', 5)
    output_audio = get_blob_rolling_window(blob, filename, folder)

    output_audio.export(filename, format='wav')

    return model_suite.check_for_wakeword(filename, target_wakeword)
