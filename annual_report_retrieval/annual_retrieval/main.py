from IPO_retrieval import *
from pdftotext import *
from pairing import *
import datetime

import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--download', action='store_true', default=True, help='')
parser.add_argument('--convert', action='store_true', default=False, help='')
parser.add_argument('--pair', action='store_true', default=False, help='')

if __name__ == '__main__':
    config = parser.parse_args()
    
    ch_save_path = r'IPO_retrieval/c'
    en_save_path = r'IPO_retrieval/e'
    ch_converted_path = r'IPO_retrieval/c_converted'
    en_converted_path = r'IPO_retrieval/e_converted'
    ch_align_path = r'IPO_retrieval/c_aligned'
    en_align_path = r'IPO_retrieval/e_aligned'
    type_of_doc = 'annual_report'

    start_date = datetime.datetime(year = 2017, month = 10, day = 1)
    end_date = datetime.datetime(year = 2017, month = 10, day = 18)

    if config.download:
        download(ch_save_path, en_save_path, start_date, end_date, type_of_doc)
    if config.convert:
        pdftotext(ch_save_path, en_save_path, ch_converted_path, en_converted_path)
    if config.pair:
        pair(en_converted_path, ch_converted_path, en_align_path, ch_align_path)


