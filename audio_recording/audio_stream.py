import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
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

        print(len(frames))
        print(excess_frames)

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


if __name__ == '__main__':
    accept_stream()
