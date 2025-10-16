# ew_platformasi/core/models.py
from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any, Dict
from core.data_models import ETPlatformu, Teknik, Radar, Senaryo, Gorev


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

    def refresh_data(self, new_data: List[Any], **kwargs):
        self.beginResetModel()
        self._data = new_data
        self._handle_extra_args(**kwargs)
        self.endResetModel()

    def _handle_extra_args(self, **kwargs):
        pass # Alt sınıflar override edebilir


class PlatformTableModel(BaseTableModel):
    def __init__(self, data: List[ETPlatformu] = None):
        super().__init__(data)
        self._headers = ["Platform Adı", "Açıklama"]

    def get_display_data(self, item: ETPlatformu, column: int) -> str:
        return [item.adi, item.aciklama][column]


class RadarTableModel(BaseTableModel):
    def __init__(self, data: List[Radar] = None):
        super().__init__(data)
        self._headers = ["Adı", "ELNOT", "Üretici", "Bant", "Görev Tipi"]

    def get_display_data(self, item: Radar, column: int) -> str:
        return [item.adi, item.elnot, item.uretici, item.frekans_bandi, item.gorev_tipi][column]


class TeknikTableModel(BaseTableModel):
    def __init__(self, data: List[Teknik] = None):
        super().__init__(data)
        self._headers = ["Adı", "Kategori", "İlişkili Platform"]
        self._platform_map = {}

    def get_display_data(self, item: Teknik, column: int) -> str:
        platform_adi = self._platform_map.get(item.platform_id, "Belirtilmemiş")
        return [item.adi, item.kategori, platform_adi][column]

    def _handle_extra_args(self, **kwargs):
        if 'platform_map' in kwargs:
            self._platform_map = kwargs['platform_map']


class SenaryoTableModel(BaseTableModel):
    def __init__(self, data: List[Senaryo] = None):
        super().__init__(data)
        self._headers = ["Senaryo Adı", "Tarih", "Platform", "Hedef Radar", "Sonuç"]
        self._platform_map = {}
        self._radar_map = {}

    def get_display_data(self, item: Senaryo, column: int) -> str:
        platform_adi = self._platform_map.get(item.et_platformu_id, "Bilinmiyor")
        radar_adi = self._radar_map.get(item.radar_id, "Bilinmiyor")
        return [item.adi, item.tarih_iso, platform_adi, radar_adi, item.sonuc_nitel][column]

    def _handle_extra_args(self, **kwargs):
        if 'platform_map' in kwargs:
            self._platform_map = kwargs['platform_map']
        if 'radar_map' in kwargs:
            self._radar_map = kwargs['radar_map']


class GorevTableModel(BaseTableModel):
    def __init__(self, data: List[Gorev] = None):
        super().__init__(data)
        self._headers = ["Görev Adı", "Görev Tarihi", "Sorumlu Personel", "Senaryo Sayısı"]

    def get_display_data(self, item: Gorev, column: int) -> str:
        if column == 0: return item.adi
        if column == 1: return item.gorev_tarihi_iso
        if column == 2: return item.sorumlu_personel
        if column == 3: return str(len(item.senaryo_id_list))
        return ""


class GorevSenaryoTableModel(QAbstractTableModel):
    def __init__(self, data: List[Senaryo] = None, radar_map: Dict = None, teknik_map: Dict = None):
        super().__init__()
        self._data = data or []
        self._radar_map = radar_map or {}
        self._teknik_map = teknik_map or {}
        self._headers = ["Senaryo Adı", "Hedef Radar", "Uygulanan EKT'ler (Sıra, Süre)", "Sonuç"]

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            senaryo = self._data[index.row()]
            col = index.column()
            if col == 0:
                return senaryo.adi
            if col == 1:
                return self._radar_map.get(senaryo.radar_id, "Bilinmiyor")
            if col == 2:
                teknik_strings = []
                sorted_uygulamalar = sorted(senaryo.uygulanan_teknikler, key=lambda u: u.sira)
                for uygulama in sorted_uygulamalar:
                    teknik_adi = self._teknik_map.get(uygulama.teknik_id, "Bilinmeyen Teknik")
                    teknik_strings.append(f"{uygulama.sira}. {teknik_adi} ({uygulama.sure_sn}sn)")
                return ", ".join(teknik_strings) if teknik_strings else "Teknik Yok"
            if col == 3:
                return senaryo.sonuc_nitel
        return None

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def refresh_data(self, new_data: List[Senaryo], radar_map: Dict, teknik_map: Dict):
        self.beginResetModel()
        self._data = new_data
        self._radar_map = radar_map
        self._teknik_map = teknik_map
        self.endResetModel()