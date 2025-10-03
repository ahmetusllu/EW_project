
# ew_platformasi/viewmodels/library_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt # <-- ADD Qt HERE
from core.data_manager import DataManager
from core.models import RadarTableModel, TeknikTableModel
from core.data_models import Radar, Teknik

class LibraryViewModel(QObject):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self._data_manager = data_manager

        # 1. Asıl veri modellerini oluştur
        self._radars_source_model = RadarTableModel()
        self._teknikler_source_model = TeknikTableModel()

        # 2. Arayüzde kullanılacak olan Filtre/Sıralama Proxy Modellerini oluştur
        self.radars_proxy_model = QSortFilterProxyModel()
        self.radars_proxy_model.setSourceModel(self._radars_source_model)
        self.radars_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.radars_proxy_model.setFilterKeyColumn(-1)  # Tüm sütunlarda ara

        self.teknikler_proxy_model = QSortFilterProxyModel()
        self.teknikler_proxy_model.setSourceModel(self._teknikler_source_model)
        self.teknikler_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.teknikler_proxy_model.setFilterKeyColumn(-1)  # Tüm sütunlarda ara

        # DataManager'dan gelen sinyalleri dinle ve asıl modelleri güncelle
        self._data_manager.radarlar_changed.connect(self._update_radars_model)
        self._data_manager.teknikler_changed.connect(self._update_teknikler_model)

        # İlk veriyi yükle
        self._update_radars_model()
        self._update_teknikler_model()

    def _update_radars_model(self):
        """DataManager'dan en güncel radar listesini alıp asıl modeli besler."""
        self._radars_source_model.refresh_data(self._data_manager.radarlar)

    def _update_teknikler_model(self):
        """DataManager'dan en güncel teknik listesini alıp asıl modeli besler."""
        self._teknikler_source_model.refresh_data(self._data_manager.teknikler)

    def set_radar_filter(self, text: str):
        """Radar tablosu için filtre metnini ayarlar."""
        self.radars_proxy_model.setFilterFixedString(text)

    def set_teknik_filter(self, text: str):
        """Teknik tablosu için filtre metnini ayarlar."""
        self.teknikler_proxy_model.setFilterFixedString(text)

    def get_item_from_proxy_index(self, proxy_index, proxy_model):
        """Proxy model index'inden asıl veri nesnesini alır."""
        source_index = proxy_model.mapToSource(proxy_index)
        source_model = proxy_model.sourceModel()
        return source_model.get_item_by_index(source_index)

    def save_item(self, item):
        self._data_manager.save_item(item)

    def delete_item(self, item):
        item_id = getattr(item, f"{item.__class__.__name__.lower()}_id")
        self._data_manager.delete_item_by_id(item_id, type(item))