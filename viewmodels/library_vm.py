# ew_platformasi/viewmodels/library_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import RadarTableModel, TeknikTableModel
from core.data_models import Radar, Teknik, Senaryo
from typing import List


class LibraryViewModel(QObject):
    status_updated = Signal(str)

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self._data_manager = data_manager
        self._data_manager.status_updated.connect(self.status_updated)

        self._radars_source_model = RadarTableModel()
        self.radars_proxy_model = QSortFilterProxyModel()
        self.radars_proxy_model.setSourceModel(self._radars_source_model)
        self.radars_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.radars_proxy_model.setFilterKeyColumn(-1)

        self._teknikler_source_model = TeknikTableModel()
        self.teknikler_proxy_model = QSortFilterProxyModel()
        self.teknikler_proxy_model.setSourceModel(self._teknikler_source_model)
        self.teknikler_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.teknikler_proxy_model.setFilterKeyColumn(-1)

        self._data_manager.radarlar_changed.connect(self._update_radars_model)
        self._data_manager.teknikler_changed.connect(self._update_teknikler_model)
        self._data_manager.senaryolar_changed.connect(self._on_senaryolar_changed)

        self._update_radars_model()
        self._update_teknikler_model()

    def _update_radars_model(self):
        self._radars_source_model.refresh_data(self._data_manager.radarlar)

    def _update_teknikler_model(self):
        self._teknikler_source_model.refresh_data(self._data_manager.teknikler)

    def _on_senaryolar_changed(self):
        pass

    def set_radar_filter(self, text: str):
        self.radars_proxy_model.setFilterFixedString(text)

    def set_teknik_filter(self, text: str):
        self.teknikler_proxy_model.setFilterFixedString(text)

    def get_item_from_proxy_index(self, proxy_index, proxy_model):
        source_index = proxy_model.mapToSource(proxy_index)
        return proxy_model.sourceModel().get_item_by_index(source_index)

    def save_item(self, item):
        self._data_manager.save_item(item)

    def delete_item(self, item):
        item_id = getattr(item, f"{type(item).__name__.lower()}_id")
        self._data_manager.delete_item_by_id(item_id, type(item))

    def duplicate_item(self, item):
        self._data_manager.duplicate_item(item)

    def get_senaryos_for_radar(self, radar_id: str) -> list[Senaryo]:
        return [s for s in self._data_manager.senaryolar if s.radar_id == radar_id]

    def item_exists(self, item_id: str, item_type: type) -> bool:
        list_ref, _, _ = self._data_manager._get_list_ref(item_type)
        if list_ref is None:
            return False
        id_field = f"{item_type.__name__.lower()}_id"
        return any(getattr(item, id_field) == item_id for item in list_ref)

    # --- YENİ EKLENEN METOTLAR ---
    def export_teknikler(self, teknik_ids: List[str], path: str):
        """Seçilen teknikleri dışa aktarır."""
        teknikler_to_export = [t for t in self._data_manager.teknikler if t.teknik_id in teknik_ids]
        if teknikler_to_export:
            self._data_manager.export_teknikler_to_xml(teknikler_to_export, path)
        else:
            self.status_updated.emit("Dışa aktarılacak teknik seçilmedi.")

    def import_teknikler(self, paths: List[str]):
        """Seçilen XML dosyalarından teknikleri içe aktarır."""
        if not paths:
            return

        total_imported = 0
        for path in paths:
            imported = self._data_manager.import_teknikler_from_xml(path)
            total_imported += len(imported)

        # DataManager'ın kendi sinyali zaten status bar'ı güncelliyor.
        # İstersek burada ek bir özet mesajı da yayınlayabiliriz.
        if total_imported > 0:
            self.status_updated.emit(f"Toplam {len(paths)} dosyadan içe aktarma işlemi tamamlandı.")
    # ------------------------------