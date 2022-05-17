import numpy as np


def dummy_detection(audio_file):
    """
    """
    rand_num = np.random.random()

    if rand_num < 0.05:
        return 'wakeword'

    else:
        return 'none_detected'
