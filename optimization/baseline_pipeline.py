"""Baseline strategy; direct execution runs the full pipeline with this strategy."""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.config import KEY,COUNTS

def summarize_employees(d):
    result=None
    for c in COUNTS:
        one=d.groupby(KEY,as_index=False)[c].sum()
        result=one if result is None else result.merge(one,on=KEY,validate='one_to_one')
    return result

if __name__=="__main__":
    from src.pipeline import main
    main(["--mode","baseline"]+sys.argv[1:])
