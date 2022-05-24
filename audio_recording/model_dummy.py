import numpy as np
import boto3
import os
import time
import tensorflow as tf
import keras.backend as K
import librosa
from sklearn import preprocessing

"""
PRE DEPLOYMENT TODOs

1. Get anchor vectors
2. Solidify integration of anchor vectors
3. Integrate preprocessing pipeline
4. Integrate anchor-case generation
5. Try end-to-end
"""

def download_latest_model(model_name, local_dir, s3_prefix):
    """
    Gets latest version of the models from s3
    """
    lcl_path = os.path.join(local_dir, model_name)
    s3_path = os.path.join(s3_prefix, model_name)

    if not os.path.exists(lcl_path):
        lcl_mtime = 0
    else:
        lcl_mtime = os.path.getmtime(lcl_path)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('fourthbrain-mc-ab-final')
    objs = bucket.objects.filter(Prefix=s3_path)

    s3_mtime = [time.mktime(x.last_modified.timetuple()) for x in objs][0]

    if s3_mtime < lcl_mtime:
        print('local file newer. Skipping')
        return

    print(f'downloading {s3_path} to {lcl_path}')
    bucket.download_file(s3_path, lcl_path)


def load_model(local_dir, model_name):
    """
    """
    model_path = os.path.join(local_dir, model_name)
    return tf.keras.models.load_model(model_path, compile=False,
                                      custom_objects={"K": K})



class FakeVectorGenerator:

    def __init__(self):
        pass

    def predict(self, preprocessed_audio):
        return np.random.random(128)


class FakeComparisonModel():

    def __init__(self):
        pass

    def predict_same_word(self, vec1, vec2):
        return np.random.random() < 0.25


class ModelWrapper:

    def __init__(self, vector_generator, comparison_model):
        self.vec_gen = vector_generator
        self.compare = comparison_model
        self.floor_const = 87
        self.active_folder = 'active_recordings'
        self.conf_thresh = 0.5
        # self.vec_dict = self._initiate_vector_dicionary()
        self.vec_dict = {'nullvec': np.random.random(128)}

    def load_audio_file(self, fpath):
        """
        Loads audio files form filepath

        :param fpath: path to file
        """
        # I don't know if this is better than handing off the audio objects.
        # I don't know how you're openning them
        with open(fpath, 'rb') as f:
            return f

    def preprocess_audio_clip(self, audio_clip):
        """
        """
        # I presume you'll have a preprocessing step.
        # Just doing a passthrough for now
        return audio_clip

    def generate_new_mean_vector(self, name):
        """
        Generates new mean vector from training examples, adds to dictionary

        :param fpaths: The list of filepaths
        :param name: The name of the wakeword

        :returns None:
        """
        # We can do this as a raw file handoff as well, not sure what's preferred
        # clips = [self.load_audio_file(f) for f in fpaths]
        target_dir = os.path.join('raw_audio', name)
        anchor_spectrums = self._load_audio_files(target_dir)
        anchor_features = [self.vec_gen(np.expand_dims(anc, 0)) for anc in anchor_spectrums]
        anchor = sum(anchor_features)/len(anchor_features)
        # I think we should maybe also save the vectors somewhere so that we
        # don't lose them on reboot? But maybe we don't care

        self.vec_dict[name] = anchor

    def _convert_wav_to_melSpectrogram(self, wav_file):
        # number of samples in a window per fft
        n_fft = 2048
        hop_length = 256
        signal, sr = librosa.core.load(wav_file)
        mel_spect = librosa.feature.melspectrogram(y=signal, sr=sr, hop_length=hop_length,
     n_fft=n_fft)
        mel_spect = librosa.power_to_db(mel_spect, ref=np.max)
        mel_spect = np.abs(mel_spect)
        return mel_spect


    def _initiate_vector_dicionary(self):
        """
        This should have some code for building a dictionary of the default
        wakewords and their vectors
        format {<name>:<vector>}
        """
        # This shoudl initiate with some locally stored examples
        # Code here is simple demo
        return {k: self.vec_gen.predict([]) for k in ['hello_fourthbrain', 'dummy_too']}

    def furnish_wakewords(self):
        """
        Gives the active wakewords
        """
        wakewords = list(self.vec_dict.keys())
        wakewords.sort()
        return wakewords

    def _prepare_features_from_filename(self, filename):
      frame_spectrums = self._load_audio_files(os.path.join(self.active_folder, filename))
      frame_features = [self.vec_gen(np.expand_dims(frame, 0)) for frame in frame_spectrums]
      mean_features = sum(frame_features)/len(frame_features)
      frame_features += [mean_features]
      return frame_features

    def check_for_wakeword(self, audio_filename, anchor_name):
        """
        Checks for the wakeword
        """
        prepped = self._prepare_features_from_filename(audio_filename)
        target_vec = self.vec_dict[anchor_name]

        if self.compare([prepped, target_vec]) > self.conf_thresh:
            return name
        return 'none_detected'

    def to_3_channels(self, spectro):
      xi = spectro[:60, :]
      xi = np.expand_dims(xi, axis=2)
      for i in range(1,3):
        xy = spectro[i*30 : (i+2)*30, :]
        xy = np.expand_dims(xy, axis=2)
        xi = np.dstack((xi, xy))
      return xi

    def _load_audio_files(self, dirname):
        """
        """
        floor_const = self.floor_const

        X = []
        if '.wav' in dirname:
            dirname, filename = dirname.split('/')
            audio_files = os.listdir(dirname)
            audio_files = [a for a in audio_files if a == filename]

        else:
            audio_files = os.listdir(dirname)
            audio_files = [a for a in audio_files if not a.startswith('.') ]  # ignoring any hidden files in the read directory

        if len(audio_files) > 0:
          for filename in audio_files:
            spectro = self._convert_wav_to_melSpectrogram(os.path.join(dirname, filename))
            spectro = preprocessing.normalize(spectro)
            frames = spectro.shape[1] / floor_const
            if frames >= 3:
              spectro = spectro[:, -3 * floor_const:]   # taking only the last 3 secs of the audio
              for i in range(0, 255, 43):
                frame = spectro[:,i:i+floor_const]   # creating 5 frames for 3 secs audio
                if frame.shape[1] == floor_const:
                  X += [self.to_3_channels(frame)]
            elif frames >= 2:
              spectro = spectro[:, -2 * floor_const:]
              for i in range(0, 171, 43):
                frame = spectro[:,i:i+floor_const]   # creating 3 frames for 2 secs audio
                if frame.shape[1] == floor_const:
                  X += [self.to_3_channels(frame)]
            elif frames >= 1:
              spectro = spectro[:, -132:]
              for i in range(0, 130, 43):
                frame = spectro[:,i:i+floor_const]
                if frame.shape[1] == floor_const:
                  X += [self.to_3_channels(frame)]
            else:
                pad_val = floor_const - spectro.shape[1]
                frame = np.pad(spectro, (0, pad_val))
                if frame.shape[1] == floor_const:
                  X += [self.to_3_channels(frame)]

        return np.array(X)
