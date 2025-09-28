from __future__ import annotations
from typing import Optional, Tuple
import pandas as pd
from .dataset_io import read_two_columns
from .source import Source, iter_source_files


#Для пункта 4 принимает дату и возвращает дата, value or none
def get_value(target_date: pd.Timestamp, source: Source):
    td = pd.to_datetime(target_date.date())  # нормализация к дате
    for path in iter_source_files(source):
        df = read_two_columns(path)
        row = df.loc[df["date"] == td]
        if not row.empty:
            return (td, float(row["value"].iloc[0]))
    return None
