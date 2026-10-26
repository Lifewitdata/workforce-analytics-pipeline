"""Read each monthly file and union rows without silent deduplication."""
import logging
import pandas as pd
from src.config import RAW
from src.quality_checks import check

def log(name, frame):
    logging.info('%s: %s rows, %s columns', name, len(frame), len(frame.columns))

def read_union(folder):
    frames=[]
    for p in sorted((RAW/folder).glob('*.csv')):
        f=pd.read_csv(p)
        month=p.stem[-7:]
        pd.Period(month,freq='M')
        if folder=='employees':
            check('File month '+p.name,f.report_month.eq(month).all())
        else:
            check('File cohort '+p.name,f.apply_date.astype(str).str[:7].eq(month).all())
        log('read '+p.name,f);frames.append(f)
    if not frames: raise ValueError(f'No CSV inputs in {folder}')
    result=pd.concat(frames,ignore_index=True);log('union '+folder,result);return result
