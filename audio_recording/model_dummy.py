import numpy as np


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
        self.vec_dict = self.initiate_vector_dicionary()

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

    def generate_new_mean_vector(self, fpaths, name):
        """
        Generates new mean vector from training examples, adds to dictionary

        :param fpaths: The list of filepaths
        :param name: The name of the wakeword

        :returns None:
        """
        # We can do this as a raw file handoff as well, not sure what's preferred
        clips = [self.load_audio_file(f) for f in fpaths]
        preprocessed_clips = [self.preprocess_audio_clip(c) for c in clips]
        vecs = np.array([self.vec_gen.predict(a) for a in preprocessed_clips])
        mean_vec = vecs.mean(axis=0)
        # I think we should maybe also save the vectors somewhere so that we
        # don't lose them on reboot? But maybe we don't care

        self.vec_dict[name] = mean_vec

    def initiate_vector_dicionary(self):
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

    def check_for_wakeword(self, audio, name):
        """
        Checks for the wakeword
        """
        prepped = self.preprocess_audio_clip(audio)
        target_vec = self.vec_dict[name]

        if self.compare.predict_same_word(prepped, target_vec):
            return name
        return 'none_detected'
