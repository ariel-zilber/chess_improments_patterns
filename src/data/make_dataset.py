# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import os

from src.data.fics_dataset import  FICSDatasetBuilder
from src.data import kaggle_utils

def fics_build(project_dir):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')
    BUILD_FICS_MIN_YEAR = int(os.getenv('BUILD_FICS_MIN_YEAR'))
    BUILD_FICS_MAX_YEAR =int( os.getenv('BUILD_FICS_MAX_YEAR'))
    BUILD_FICS_GAME_TYPE =  os.getenv('BUILD_FICS_GAME_TYPE')
    years=[y for y in range(BUILD_FICS_MIN_YEAR,BUILD_FICS_MAX_YEAR+1)]
    FICSDatasetBuilder(str(project_dir),BUILD_FICS_GAME_TYPE,years).build()

def lichess_download(project_dir):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Download lichess existing dataset')
    for path in [
        f'{project_dir}/data',
        f'{project_dir}/data/lichess',
        f'{project_dir}/data/lichess/raw',
        f'{project_dir}/data/lichess/interim',
        f'{project_dir}/data/lichess/proccessed',
        f'{project_dir}/data/lichess/external',
    ]:
        if not os.path.exists(path):
            os.mkdir(path)
    #
    kaggle_utils.download_from_kaggle("arielzilber/chess-games-for-uni-course",
                                      str(project_dir)+"/data/lichess/external/")
        

def fics_download(project_dir):
    logger = logging.getLogger(__name__)
    logger.info('Download fics existing dataset')
    for path in [
        f'{project_dir}/data',
        f'{project_dir}/data/fics',
        f'{project_dir}/data/fics/raw',
        f'{project_dir}/data/fics/interim',
        f'{project_dir}/data/fics/proccessed',
        f'{project_dir}/data/fics/external',
    ]:
        if not os.path.exists(path):
            os.mkdir(path)
    #arielzilber/fcis-standard-2009-to-2023
    kaggle_utils.download_from_kaggle("arielzilber/fcis-standard-2009-to-2023",
                                      str(project_dir)+"/data/fics/external/")
        

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    #
    BUILD_FICS_ENABLED = (os.getenv('BUILD_FICS_ENABLED')=="true")
    if BUILD_FICS_ENABLED:
        fics_build(project_dir)
    
    #
    DOWNLOAD_FICS_ENABLED = (os.getenv('DOWNLOAD_FICS_ENABLED')=="true")
    if DOWNLOAD_FICS_ENABLED:
        fics_download(project_dir)
    
    #
    DOWNLOAD_LICHESS_ENABLED = (os.getenv('DOWNLOAD_LICHESS_ENABLED')=="true")
    if DOWNLOAD_LICHESS_ENABLED:
        lichess_download(project_dir)
