# ew_platformasi/core/models.py
from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any, Dict
from core.data_models import Teknik, Radar, Senaryo


# Bu dosya, UI tablolarının (QTableView) veri kaynaklarını tanımlar.
# DataManager'dan gelen ham veri listelerini alıp tabloların anlayacağı dile çevirirler.

class RadarTableModel(QAbstractTableModel):
    def __init__(self, data: List[Radar] = None):
        super().__init__()
        self._data = data or []
        self._headers = ["Adı", "Üretici", "Bant", "Görev Tipi"]

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            radar = self._data[index.row()]
            col = index.column()
            if col == 0: return radar.adi
            if col == 1: return radar.uretici
            if col == 2: return radar.frekans_bandi
            if col == 3: return radar.gorev_tipi
        return None

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def get_item_by_index(self, index: QModelIndex) -> Radar | None:
        if index.isValid() and 0 <= index.row() < len(self._data): return self._data[index.row()]
        return None

    def refresh_data(self, new_data: List[Radar]):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()


class TeknikTableModel(QAbstractTableModel):
    def __init__(self, data: List[Teknik] = None):
        super().__init__()
        self._data = data or []
        self._headers = ["Adı", "Kategori"]

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            teknik = self._data[index.row()]
            col = index.column()
            if col == 0: return teknik.adi
            if col == 1: return teknik.kategori
        return None

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def get_item_by_index(self, index: QModelIndex) -> Teknik | None:
        if index.isValid() and 0 <= index.row() < len(self._data): return self._data[index.row()]
        return None

    def refresh_data(self, new_data: List[Teknik]):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    # Bu sınıfı core/models.py dosyasının sonuna ekleyin

class SenaryoTableModel(QAbstractTableModel):
    def __init__(self, data: List[Senaryo] = None):
        super().__init__()
        self._data = data or []
        self._headers = ["Senaryo Adı", "Tarih", "Konum", "Sonuç"]

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            item = self._data[index.row()]
            col = index.column()
            if col == 0: return item.adi
            if col == 1: return item.tarih_iso
            if col == 2: return item.konum
            if col == 3: return item.sonuc_nitel
        return None

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def get_item_by_index(self, index: QModelIndex) -> Senaryo | None:
        if index.isValid() and 0 <= index.row() < len(self._data): return self._data[index.row()]
        return None

    def refresh_data(self, new_data: List[Senaryo]):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    # BU SINIFI KOPYALAYIP DOSYANIN SONUNA EKLEYİN

    class SenaryoTableModel(QAbstractTableModel):
        def __init__(self, data: List[Senaryo] = None):
            super().__init__()
            self._data = data or []
            self._headers = ["Senaryo Adı", "Tarih", "Konum", "Sonuç"]

        def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole:
                item = self._data[index.row()]
                col = index.column()
                if col == 0: return item.adi
                if col == 1: return item.tarih_iso
                if col == 2: return item.konum
                if col == 3: return item.sonuc_nitel
            return None

        def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
            return len(self._data)

        def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
            return len(self._headers)

        def headerData(self, section: int, orientation: Qt.Orientation,
                       role: int = Qt.ItemDataRole.DisplayRole) -> Any:
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            return None

        def get_item_by_index(self, index: QModelIndex) -> Senaryo | None:
            if index.isValid() and 0 <= index.row() < len(self._data): return self._data[index.row()]
            return None

        def refresh_data(self, new_data: List[Senaryo]):
            self.beginResetModel()
            self._data = new_data
            self.endResetModel()

