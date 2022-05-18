import wave
import os
from audio_recording import model_dummy as model
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.utils import make_chunks
import pyaudio
import io

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
# RATE = 44100
RATE = 48000
WINDOW_SECS = 3
WINDOW_SLIDE = 1
WAVE_OUTPUT_FILENAME = "voice.wav"
MAX_RECORD_SECONDS = 300

p = pyaudio.PyAudio()


def accept_stream():
    """
    Accepts stream from front-end
    """
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    max_frames = int(RATE / CHUNK * WINDOW_SECS)
    max_frames = 100

    slide_interval = int(RATE / CHUNK * WINDOW_SLIDE)

    for i in range(0, 10000):

        data = stream.read(CHUNK)
        frames.append(data)
        excess_frames = len(frames) - max_frames

        # print(len(frames))
        # print(excess_frames)

        if excess_frames > 0:
            frames = frames[excess_frames:]

        if i % slide_interval == 0:
            save_file(WAVE_OUTPUT_FILENAME, frames)


def save_file(output_filename, frames):
    """
    Saves running window file

    :param output_filename: filename to save to
    :param frames: list of audio chunks

    :returns: None, saves file
    """
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def save_new_wakeword(blob, filename):
    """
    saves new wakeword
    """

    s = io.BytesIO(blob)
    audio = AudioSegment.from_file(s, sample_width=2, frame_rate=RATE, format='wav',
                                channels=2)

    folder = f'raw_audio/{filename}/'

    if not os.path.isdir(folder):
        os.mkdir(folder)

    chunks = split_on_silence (
    # Use the loaded audio.
    audio, min_silence_len = 500, silence_thresh = -40
    )

    for i, c in enumerate(chunks):
        c.export(os.path.join(folder, str(i) + '.wav'), format='wav')


def save_blob_from_js(blob, filename):
    """
    """


    s = io.BytesIO(blob)
    audio = AudioSegment.from_file(s, sample_width=2, frame_rate=RATE, format='wav',
                                channels=2)

    if os.path.exists(filename):
        # print('exists')
        existing_audio = AudioSegment.from_file(filename, sample_width=2,
                                                frame_rate=RATE, format='wav',
                                                channels=2)

        new_audio = existing_audio + audio
    else:
        new_audio = AudioSegment.silent(duration=100000) + audio

    chunks = make_chunks(new_audio, 100)
    output_audio = AudioSegment.silent(duration=0)
    for c in chunks[-20:]:
        output_audio += c

    output_audio.export(filename, format='wav')

    return model.dummy_detection(output_audio)

    # new_audio.export(filename, format='wav')

    # with open(filename, 'wb') as f:
        # f.write(blob)
    # wf = wave.open(filename, 'wb')
    # wf.setnchannels(1)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(blob)
    # wf.close()




if __name__ == '__main__':
    accept_stream()
