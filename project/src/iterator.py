from __future__ import annotations
from typing import Optional, Tuple
import pandas as pd
from .dataset_io import read_two_columns
from .source import Source, iter_source_files

#В один файл + итерация по датам
class KztIterator:
    
    def __init__(self, source: Source):
        dfs = [read_two_columns(p) for p in iter_source_files(source)]
        if dfs:
            all_df = pd.concat(dfs, ignore_index=True)
            all_df = all_df.drop_duplicates(subset=["date"])
            all_df = all_df.sort_values("date")
            all_df = all_df.reset_index(drop=True)

        else:
            all_df = pd.DataFrame(columns=["date", "value"])
        self._df = all_df
        self._i = 0

    def next(self):
        if self._i >= len(self._df):
            return None
        row = self._df.iloc[self._i]
        self._i += 1
        return (pd.to_datetime(row["date"]), float(row["value"]))
