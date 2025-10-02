from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
from PySide6 import QtWidgets, QtCore

from src.dataset_io import save_XY
from src.splitters import split_by_year, split_by_week
from src.source import Source
from src.query import get_value
from src.annotate import annotate_csv, annotate_dir

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab3 KZT→RUB GUI")
        self.resize(820, 480)

        # state
        self.input_dir: Path | None = None
        self.input_csv: Path | None = None
        self.output_dir: Path | None = None

        # widgets
        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        v = QtWidgets.QVBoxLayout(root)

        # Block: source folder + csv
        grp_src = QtWidgets.QGroupBox("Исходный датасет")
        v.addWidget(grp_src)
        g = QtWidgets.QGridLayout(grp_src)

        self.le_input_dir = QtWidgets.QLineEdit(); self.le_input_dir.setReadOnly(True)
        btn_pick_dir = QtWidgets.QPushButton("Выбрать папку…")
        btn_pick_dir.clicked.connect(self.pick_input_dir)

        self.cb_csv = QtWidgets.QComboBox()
        self.cb_csv.currentIndexChanged.connect(self._on_csv_change)

        g.addWidget(QtWidgets.QLabel("Папка:"), 0, 0)
        g.addWidget(self.le_input_dir, 0, 1)
        g.addWidget(btn_pick_dir, 0, 2)
        g.addWidget(QtWidgets.QLabel("CSV:"), 1, 0)
        g.addWidget(self.cb_csv, 1, 1, 1, 2)

        # Block: actions
        grp_actions = QtWidgets.QGroupBox("Операции")
        v.addWidget(grp_actions)
        h = QtWidgets.QHBoxLayout(grp_actions)

        btn_annot_src = QtWidgets.QPushButton("Аннотация исходного CSV…")
        btn_annot_src.clicked.connect(self.make_src_annotation)
        btn_build = QtWidgets.QPushButton("Собрать датасет (X/Y, годы, недели) + аннотации…")
        btn_build.clicked.connect(self.build_datasets)

        h.addWidget(btn_annot_src)
        h.addWidget(btn_build)
        h.addStretch(1)

        # Block: query by date визуал
        grp_query = QtWidgets.QGroupBox("Запрос по дате")
        v.addWidget(grp_query)
        ql = QtWidgets.QGridLayout(grp_query)

        self.date_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)

        self.src_mode = QtWidgets.QComboBox()
        self.src_mode.addItems(["RAW", "BY_YEAR", "BY_WEEK"])

        self.le_query_root = QtWidgets.QLineEdit(); self.le_query_root.setReadOnly(True)
        btn_pick_query_root = QtWidgets.QPushButton("Папка источника…")
        btn_pick_query_root.clicked.connect(self.pick_query_root)

        btn_get = QtWidgets.QPushButton("Получить данные")
        btn_get.clicked.connect(self.do_query)
        self.lbl_result = QtWidgets.QLabel("—")

        ql.addWidget(QtWidgets.QLabel("Дата:"), 0, 0)
        ql.addWidget(self.date_edit, 0, 1)
        ql.addWidget(QtWidgets.QLabel("Источник:"), 0, 2)
        ql.addWidget(self.src_mode, 0, 3)
        ql.addWidget(self.le_query_root, 1, 0, 1, 3)
        ql.addWidget(btn_pick_query_root, 1, 3)
        ql.addWidget(btn_get, 2, 0)
        ql.addWidget(self.lbl_result, 2, 1, 1, 3)

        v.addStretch(1)

    #пункт 1. 
    def pick_input_dir(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку с исходным датасетом")
        if not path:
            return
        self.input_dir = Path(path)
        self.le_input_dir.setText(path)
        self.cb_csv.clear()
        csvs = sorted(self.input_dir.glob("*.csv"))
        if not csvs:
            QtWidgets.QMessageBox.warning(self, "Нет CSV", "В выбранной папке нет *.csv")
            return
        for p in csvs:
            self.cb_csv.addItem(p.name, str(p))
        self._on_csv_change()

    def _on_csv_change(self):
        idx = self.cb_csv.currentIndex()
        self.input_csv = None if idx < 0 else Path(self.cb_csv.currentData())

   #Создание аннотации
    def make_src_annotation(self):
        if self.input_csv is None:
            QtWidgets.QMessageBox.warning(self, "Не выбран CSV", "Сначала выберите исходный CSV.")
            return
        out, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Куда сохранить аннотацию", "annotation_src.json", "JSON (*.json)")
        if not out:
            return
        annotate_csv(self.input_csv, Path(out))
        QtWidgets.QMessageBox.information(self, "Готово", f"Аннотация сохранена:\n{out}")

    def build_datasets(self):
        
        dest = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку назначения")
        if not dest:
            return
        self.output_dir = Path(dest)

        # X/Y
        save_XY(self.input_csv, self.output_dir / "X.csv", self.output_dir / "Y.csv")

        # by_year / by_week
        by_year = self.output_dir / "by_year"; by_year.mkdir(parents=True, exist_ok=True)
        by_week = self.output_dir / "by_week"; by_week.mkdir(parents=True, exist_ok=True)
        split_by_year(self.input_csv, by_year)
        split_by_week(self.input_csv, by_week)

        # annotations
        annotate_csv(self.input_csv, self.output_dir / "annotation_src.json")
        annotate_dir(by_year, self.output_dir / "annotation_by_year.json")
        annotate_dir(by_week, self.output_dir / "annotation_by_week.json")

        QtWidgets.QMessageBox.information(self, "Готово", f"Данные собраны в:\n{dest}")

    def pick_query_root(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Папка источника для запроса")
        if not path:
            return
        self.le_query_root.setText(path)


  
    def do_query(self):
        mode = self.src_mode.currentText()
        root = self.le_query_root.text().strip()
       

        d = pd.Timestamp(self.date_edit.date().toString("yyyy-MM-dd"))
        src_path = Path(root)

        if mode == "RAW":
            # ожидается один CSV внутри папки
            csvs = sorted(src_path.glob("*.csv"))
            if not csvs:
                QtWidgets.QMessageBox.warning(self, "Нет CSV", "В папке нет *.csv для RAW.")
                return
            src = Source.raw(csvs[0])
        elif mode == "BY_YEAR":
            src = Source.by_year(src_path)
        else:
            src = Source.by_week(src_path)

        res = get_value(d, src)
        self.lbl_result.setText("Нет данных" if res is None else f"{res[0].date()}: {res[1]}")
