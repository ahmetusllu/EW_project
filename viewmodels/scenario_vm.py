# ew_platformasi/viewmodels/scenario_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import SenaryoTableModel
from core.data_models import Senaryo, Teknik
from typing import List

class ScenarioViewModel(QObject):
    status_updated = Signal(str)
    edit_scenario_requested = Signal(Senaryo)

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self._data_manager = data_manager

        self._source_model = SenaryoTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self._data_manager.platformlar_changed.connect(self._update_model)
        self._data_manager.radarlar_changed.connect(self._update_model)
        self._data_manager.senaryolar_changed.connect(self._update_model)
        self._data_manager.teknikler_changed.connect(self._update_model)
        self._data_manager.status_updated.connect(self.status_updated)
        self._update_model()

    def _update_model(self):
        platform_map = {p.platform_id: p.adi for p in self._data_manager.et_platformlar}
        radar_map = {r.radar_id: r.adi for r in self._data_manager.radarlar}
        self._source_model.refresh_data(
            self._data_manager.senaryolar,
            platform_map=platform_map,
            radar_map=radar_map
        )

    def get_available_data(self):
        """Formları doldurmak için gerekli tüm veriyi döndürür."""
        return self._data_manager.et_platformlar, self._data_manager.radarlar, self._data_manager.teknikler

    def get_teknikler_for_platform(self, platform_id: str) -> List[Teknik]:
        """Belirli bir platforma ait teknikleri döndürür."""
        if not platform_id:
            return []
        return [t for t in self._data_manager.teknikler if t.platform_id == platform_id]

    def set_filter(self, text: str):
        self.proxy_model.setFilterFixedString(text)

    def get_item_from_proxy_index(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self._source_model.get_item_by_index(source_index)

    def save_scenario(self, scenario: Senaryo) -> Senaryo:
        is_new = not self._data_manager.item_exists(scenario.senaryo_id, Senaryo) if scenario.senaryo_id else True
        saved_item = self._data_manager.save_item(scenario)
        if is_new:
             self.status_updated.emit(f"'{saved_item.adi}' senaryosu oluşturuldu.")
        else:
             self.status_updated.emit(f"'{saved_item.adi}' senaryosu güncellendi.")
        return saved_item

    def delete_scenario(self, scenario: Senaryo):
        self._data_manager.delete_item_by_id(scenario.senaryo_id, Senaryo)
        self.status_updated.emit(f"'{scenario.adi}' senaryosu silindi.")

    def duplicate_scenario(self, scenario: Senaryo):
        self._data_manager.duplicate_item(scenario)

    def request_edit_scenario(self, scenario: Senaryo):
        self.edit_scenario_requested.emit(scenario)

    def save_teknik(self, teknik: Teknik):
        self._data_manager.save_item(teknik)
        self.status_updated.emit(f"Yeni teknik '{teknik.adi}' kütüphaneye eklendi.")