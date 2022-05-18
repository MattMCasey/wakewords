import os


def get_available_wakewords():
    """
    """
    vecs = [x for x in os.listdir('wakewords')]
    wakewords = [x.split('.')[0] for x in vecs]

    return wakewords
