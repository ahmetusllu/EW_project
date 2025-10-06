# ew_platformasi/core/models.py
from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any
from core.data_models import Teknik, Radar, Senaryo, Gorev

class BaseTableModel(QAbstractTableModel):
    def __init__(self, data: List[Any] = None):
        super().__init__()
        self._data = data or []
        self._headers = []

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self.get_display_data(self._data[index.row()], index.column())
        return None

    def get_display_data(self, item: Any, column: int) -> str:
        raise NotImplementedError

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def get_item_by_index(self, index: QModelIndex) -> Any | None:
        if index.isValid() and 0 <= index.row() < len(self._data):
            return self._data[index.row()]
        return None

    def refresh_data(self, new_data: List[Any]):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

class RadarTableModel(BaseTableModel):
    def __init__(self, data: List[Radar] = None):
        super().__init__(data)
        self._headers = ["Adı", "Üretici", "Bant", "Görev Tipi"]

    def get_display_data(self, item: Radar, column: int) -> str:
        return [item.adi, item.uretici, item.frekans_bandi, item.gorev_tipi][column]

class TeknikTableModel(BaseTableModel):
    def __init__(self, data: List[Teknik] = None):
        super().__init__(data)
        self._headers = ["Adı", "Kategori"]

    def get_display_data(self, item: Teknik, column: int) -> str:
        return [item.adi, item.kategori][column]

class SenaryoTableModel(BaseTableModel):
    def __init__(self, data: List[Senaryo] = None):
        super().__init__(data)
        self._headers = ["Senaryo Adı", "Tarih", "Konum", "Sonuç"]

    def get_display_data(self, item: Senaryo, column: int) -> str:
        return [item.adi, item.tarih_iso, item.konum, item.sonuc_nitel][column]

class GorevTableModel(BaseTableModel):
    def __init__(self, data: List[Gorev] = None):
        super().__init__(data)
        self._headers = ["Görev Adı", "Oluşturma Tarihi", "Sorumlu Personel", "Senaryo Sayısı"]

    def get_display_data(self, item: Gorev, column: int) -> str:
        if column == 0: return item.adi
        if column == 1: return item.olusturma_tarihi_iso
        if column == 2: return item.sorumlu_personel
        if column == 3: return str(len(item.senaryo_id_list))
        return ""