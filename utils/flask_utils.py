import os


def make_folder_if_not_exist(folder):
    """
    """
    if not os.path.exists(folder):
        os.mkdir(folder)



# def get_available_wakewords():
#     """
#     """
#     vecs = [x for x in os.listdir('wakewords')]
#     wakewords = [x.split('.')[0] for x in vecs]
#
#     return wakewords
