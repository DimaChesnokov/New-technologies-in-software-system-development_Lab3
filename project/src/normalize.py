from __future__ import annotations
import pandas as pd
from pathlib import Path
from .config import DATE_FMT


#Читка csv из лаб 1 и делит на две колонки date value
def read_base(csv_path: Path):
    df = pd.read_csv(csv_path)
   
    df = df.iloc[:, :2].copy()
    df.columns = ["date", "value"]

    # строгий разбор ISO 8601
    df["date"] = pd.to_datetime(df["date"], format=DATE_FMT, errors="raise")

  
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # очистка 
    df = df.dropna(subset=["value"])
    df = df.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df
