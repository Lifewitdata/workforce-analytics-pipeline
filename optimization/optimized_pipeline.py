"""Optimized strategy; direct execution runs the full pipeline with this strategy."""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.config import KEY,COUNTS

def summarize_employees(d):
    return d[KEY+COUNTS].groupby(KEY,as_index=False)[COUNTS].sum()

if __name__=="__main__":
    from src.pipeline import main
    main(["--mode","optimized"]+sys.argv[1:])
