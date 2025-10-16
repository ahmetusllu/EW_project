# ew_platformasi/viewmodels/library_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import PlatformTableModel, RadarTableModel, TeknikTableModel
from core.data_models import ETPlatformu, Radar, Teknik, Senaryo
from typing import List


class LibraryViewModel(QObject):
    status_updated = Signal(str)

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self._data_manager = data_manager
        self._data_manager.status_updated.connect(self.status_updated)

        # Platformlar için model
        self._platformlar_source_model = PlatformTableModel()
        self.platformlar_proxy_model = QSortFilterProxyModel()
        self.platformlar_proxy_model.setSourceModel(self._platformlar_source_model)
        self.platformlar_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.platformlar_proxy_model.setFilterKeyColumn(-1)

        # Radarlar için model
        self._radars_source_model = RadarTableModel()
        self.radars_proxy_model = QSortFilterProxyModel()
        self.radars_proxy_model.setSourceModel(self._radars_source_model)
        self.radars_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.radars_proxy_model.setFilterKeyColumn(-1)

        # Teknikler için model
        self._teknikler_source_model = TeknikTableModel()
        self.teknikler_proxy_model = QSortFilterProxyModel()
        self.teknikler_proxy_model.setSourceModel(self._teknikler_source_model)
        self.teknikler_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.teknikler_proxy_model.setFilterKeyColumn(-1)

        # Sinyal bağlantıları
        self._data_manager.platformlar_changed.connect(self._update_platformlar_model)
        self._data_manager.radarlar_changed.connect(self._update_radars_model)
        self._data_manager.teknikler_changed.connect(self._update_teknikler_model)
        self._data_manager.senaryolar_changed.connect(self._on_senaryolar_changed)

        # Modelleri başlangıçta doldur
        self._update_platformlar_model()
        self._update_radars_model()
        self._update_teknikler_model()

    def _update_platformlar_model(self):
        self._platformlar_source_model.refresh_data(self._data_manager.et_platformlar)
        self._update_teknikler_model() # Teknikler tablosu platform isimlerini gösterdiği için güncellenmeli

    def _update_radars_model(self):
        self._radars_source_model.refresh_data(self._data_manager.radarlar)

    def _update_teknikler_model(self):
        platform_map = {p.platform_id: p.adi for p in self._data_manager.et_platformlar}
        self._teknikler_source_model.refresh_data(self._data_manager.teknikler, platform_map=platform_map)

    def _on_senaryolar_changed(self):
        pass

    def set_filter(self, text: str, model_type: str):
        if model_type == "platform":
            self.platformlar_proxy_model.setFilterFixedString(text)
        elif model_type == "radar":
            self.radars_proxy_model.setFilterFixedString(text)
        elif model_type == "teknik":
            self.teknikler_proxy_model.setFilterFixedString(text)

    def get_item_from_proxy_index(self, proxy_index, proxy_model):
        source_index = proxy_model.mapToSource(proxy_index)
        return proxy_model.sourceModel().get_item_by_index(source_index)

    def save_item(self, item):
        self._data_manager.save_item(item)

    def delete_item(self, item):
        item_type = type(item)
        id_field_name = f"{item_type.__name__.lower().replace('et', 'et_')}_id"
        if id_field_name == "et_platformu_id": id_field_name = "platform_id"
        item_id = getattr(item, id_field_name)
        self._data_manager.delete_item_by_id(item_id, item_type)

    def duplicate_item(self, item):
        self._data_manager.duplicate_item(item)

    def get_senaryos_for_radar(self, radar_id: str) -> list[Senaryo]:
        return [s for s in self._data_manager.senaryolar if s.radar_id == radar_id]

    def item_exists(self, item_id: str, item_type: type) -> bool:
        return self._data_manager.item_exists(item_id, item_type)

    def get_all_platforms(self) -> List[ETPlatformu]:
        return self._data_manager.et_platformlar

    def export_teknikler(self, teknik_ids: List[str], path: str):
        teknikler_to_export = [t for t in self._data_manager.teknikler if t.teknik_id in teknik_ids]
        if teknikler_to_export:
            self._data_manager.export_teknikler_to_xml(teknikler_to_export, path)
        else:
            self.status_updated.emit("Dışa aktarılacak teknik seçilmedi.")

    def import_teknikler(self, paths: List[str]):
        if not paths:
            return
        total_imported = sum(len(self._data_manager.import_teknikler_from_xml(path)) for path in paths)
        if total_imported > 0:
            self.status_updated.emit(f"Toplam {len(paths)} dosyadan içe aktarma işlemi tamamlandı.")