import os
from core.logger.logging import logger

def exists(path):
    return os.path.exists(path)


def ensure_folder(folder):
    if(exists(folder) == False):
        logger.info(f'> Creating folder at {folder}')
        os.makedirs(folder)

    return