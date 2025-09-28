from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from .dataset_io import read_two_columns
from .normalize import read_base

#json аннотация по csv - size,dats,miss,stats
def annotate_csv(input_csv: Path, out_json: Path):
    raw = pd.read_csv(input_csv).iloc[:, :2]
    cleaned = read_base(input_csv)

    n_raw = len(raw)
    n = len(cleaned)
    dmin = cleaned["date"].min()
    dmax = cleaned["date"].max()
    expected = (dmax - dmin).days + 1 if n else 0
    uniq = cleaned["date"].nunique()
    missing = max(expected - uniq, 0)

    stats = {
        "file": str(input_csv),
        "rows_raw": int(n_raw),
        "rows_clean": int(n),
        "date_min": None if dmin is pd.NaT else dmin.strftime("%Y-%m-%d"),
        "date_max": None if dmax is pd.NaT else dmax.strftime("%Y-%m-%d"),
        "expected_daily_rows": int(expected),
        "unique_dates": int(uniq),
        "missing_dates_est": int(missing),
        "value_min": None if n == 0 else float(cleaned["value"].min()),
        "value_max": None if n == 0 else float(cleaned["value"].max()),
        "value_mean": None if n == 0 else float(cleaned["value"].mean()),
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


#Анотация по всем csv в каталоге
def annotate_dir(dir_path: Path, out_json: Path):

    files = sorted(Path(dir_path).glob("*.csv"))
    total_rows = 0
    dmin = None
    dmax = None
    for p in files:
        df = read_two_columns(p)
        total_rows += len(df)
        if not df.empty:
            lo, hi = df["date"].min(), df["date"].max()
            dmin = lo if dmin is None or lo < dmin else dmin
            dmax = hi if dmax is None or hi > dmax else dmax

    data = {
        "dir": str(dir_path),
        "files_count": len(files),
        "total_rows": int(total_rows),
        "date_min": None if dmin is None else dmin.strftime("%Y-%m-%d"),
        "date_max": None if dmax is None else dmax.strftime("%Y-%m-%d"),
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
