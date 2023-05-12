import logging
import os
import warnings
from datetime import datetime
from pathlib import Path

import pytz


# warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent


current_directory = os.path.dirname(os.path.abspath(__file__))
new_folder_path = os.path.join(current_directory, "logs")

if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
  




RECORDS_DIR = BASE_DIR / 'records'
TZ = pytz.timezone('US/Eastern')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_fmt = '%(asctime)s:%(message)s'
date_fmt = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(fmt=log_fmt, datefmt=date_fmt)
file_handler = logging.FileHandler(os.path.join(current_directory, f'logs/{datetime.now().date()}_bt.log'))

file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


def customTime(*args):
    utc_dt = pytz.utc.localize(datetime.utcnow())
    converted = utc_dt.astimezone(TZ)
    return converted.timetuple()


logging.Formatter.converter = customTime
