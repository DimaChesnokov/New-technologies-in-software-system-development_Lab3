from __future__ import annotations
from pathlib import Path
import pandas as pd
from .normalize import read_base
from .config import DATE_FMT

#Файл на Каждый год в csv
def split_by_year(input_csv: Path, out_dir: Path):
 
    df = read_base(input_csv)
    files: list[Path] = []
    for year, g in df.groupby(df["date"].dt.year):
        start = g["date"].min().strftime("%Y%m%d")
        end = g["date"].max().strftime("%Y%m%d")
        p = out_dir / f"{start}_{end}.csv"
        g.to_csv(p, index=False, date_format=DATE_FMT)
        files.append(p)
    return files

#Недели сплитуем пн-вс
def split_by_week(input_csv: Path, out_dir: Path):
   
    df = read_base(input_csv)
    
    week_period = df["date"].dt.to_period("W-MON")
    files: list[Path] = []
    for _, g in df.groupby(week_period):
        start = g["date"].min().strftime("%Y%m%d")
        end = g["date"].max().strftime("%Y%m%d")
        p = out_dir / f"{start}_{end}.csv"
        g.to_csv(p, index=False, date_format=DATE_FMT)
        files.append(p)
    return files
