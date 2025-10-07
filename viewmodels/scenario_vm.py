# ew_platformasi/viewmodels/scenario_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import SenaryoTableModel
from core.data_models import Senaryo


class ScenarioViewModel(QObject):
    status_updated = Signal(str)
    edit_scenario_requested = Signal(Senaryo) # Yeni sinyal

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self._data_manager = data_manager

        # Senaryo Merkezi için modeller
        self._source_model = SenaryoTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self._data_manager.senaryolar_changed.connect(self._update_model)
        self._data_manager.status_updated.connect(self.status_updated)
        self._update_model()

    def _update_model(self):
        self._source_model.refresh_data(self._data_manager.senaryolar)

    def get_full_data_maps(self):
        """Formlardaki ID'leri isme çevirmek için haritalar döndürür."""
        radar_map = {r.radar_id: r.adi for r in self._data_manager.radarlar}
        teknik_map = {t.teknik_id: t.adi for t in self._data_manager.teknikler}
        return radar_map, teknik_map

    def get_available_radars_and_teknikler(self):
        """Yeni kayıt formundaki listeleri doldurmak için veri döndürür."""
        return self._data_manager.radarlar, self._data_manager.teknikler

    def set_filter(self, text: str):
        self.proxy_model.setFilterFixedString(text)

    def get_item_from_proxy_index(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self._source_model.get_item_by_index(source_index)

    def save_scenario(self, scenario: Senaryo):
        """Yeni senaryo kaydeder veya mevcut senaryoyu günceller."""
        is_new = not scenario.senaryo_id
        self._data_manager.save_item(scenario)
        # DataManager zaten sinyal gönderdiği için burada ayrıca emit yapmaya gerek yok.
        # Sadece status mesajını güncelleyelim.
        if is_new:
             self.status_updated.emit(f"'{scenario.adi}' senaryosu oluşturuldu.")
        else:
             self.status_updated.emit(f"'{scenario.adi}' senaryosu güncellendi.")

    def delete_scenario(self, scenario: Senaryo):
        self._data_manager.delete_item_by_id(scenario.senaryo_id, Senaryo)
        self.status_updated.emit(f"'{scenario.adi}' senaryosu silindi.")

    def duplicate_scenario(self, scenario: Senaryo):
        self._data_manager.duplicate_item(scenario)

    def request_edit_scenario(self, scenario: Senaryo):
        """Düzenleme isteğini sinyal olarak yayar."""
        self.edit_scenario_requested.emit(scenario)