# ew_platformasi/ui/dialogs/radar_history_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableView, QLineEdit,
                               QHeaderView, QAbstractItemView)
from PySide6.QtCore import QSortFilterProxyModel, Qt
from core.models import SenaryoTableModel
from core.data_models import Senaryo
from typing import List


class RadarHistoryDialog(QDialog):
    def __init__(self, radar_adi: str, senaryolar: List[Senaryo], parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"'{radar_adi}' Radarı Faaliyet Geçmişi")
        self.setMinimumSize(800, 600)

        self.source_model = SenaryoTableModel(senaryolar)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        layout = QVBoxLayout(self)

        self.search_box = QLineEdit(placeholderText="Geçmiş senaryolarda ara (ad, sonuç vb.)...")
        self.table = QTableView()
        self.table.setModel(self.proxy_model)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.search_box)
        layout.addWidget(self.table)

        self.search_box.textChanged.connect(self.proxy_model.setFilterFixedString)