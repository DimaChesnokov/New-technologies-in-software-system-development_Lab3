from pathlib import Path
import pandas as pd
from .normalize import read_base
from .config import DATE_FMT

#Делит на x.cvs, y.csv
def save_XY(input_csv: Path, x_csv: Path, y_csv: Path) -> None:
    """Разбивает исходный CSV на X.csv (даты) и Y.csv (значения)."""
    df = read_base(input_csv)
    pd.DataFrame({"date": df["date"].dt.strftime(DATE_FMT)}).to_csv(x_csv, index=False)
    pd.DataFrame({"value": df["value"].astype(float)}).to_csv(y_csv, index=False)

def read_two_columns(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path).iloc[:, :2].copy()
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], format=DATE_FMT, errors="raise")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"]).drop_duplicates(subset=["date"]).sort_values("date")
    return df
