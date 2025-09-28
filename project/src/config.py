from pathlib import Path

# Формат даты ISO 8601 без времени
DATE_FMT = "%Y-%m-%d"


ROOT = Path(".")
DATA_DIR = ROOT / "data"

RAW_CSV = DATA_DIR / "dataset_KZT.csv"   # из ЛР-1: 2 колонки (date,value)
X_CSV = DATA_DIR / "X.csv"
Y_CSV = DATA_DIR / "Y.csv"

BY_YEAR_DIR = DATA_DIR / "by_year"
BY_WEEK_DIR = DATA_DIR / "by_week"


DATA_DIR.mkdir(parents=True, exist_ok=True)
BY_YEAR_DIR.mkdir(parents=True, exist_ok=True)
BY_WEEK_DIR.mkdir(parents=True, exist_ok=True)
