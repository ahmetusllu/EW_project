# ew_platformasi/viewmodels/scenario_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import SenaryoTableModel
from core.data_models import Senaryo


class ScenarioViewModel(QObject):
    status_updated = Signal(str)

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
        self._data_manager.save_item(scenario)
        self.status_updated.emit(f"'{scenario.adi}' senaryosu kaydedildi.")

    def delete_scenario(self, scenario: Senaryo):
        self._data_manager.delete_item_by_id(scenario.senaryo_id, Senaryo)
        self.status_updated.emit(f"'{scenario.adi}' senaryosu silindi.")

    def export_scenario(self, scenario: Senaryo, path: str):
        self._data_manager.export_item(scenario, path)
        self.status_updated.emit(f"'{scenario.adi}' senaryosu dışa aktarıldı.")

    def import_scenarios(self, path: str):
        # DataManager'da tekil import var, burada çoğul import simüle edilebilir
        # Şimdilik tekil import kullanalım.
        imported_name = self._data_manager.import_item(
            path, Senaryo, self._data_manager.senaryolar,
            lambda: self._data_manager._save_all(self._data_manager.senaryolar, SENARYOLAR_XML, SENARYOLAR_XSD,
                                                 "Senaryolar"),
            self._data_manager.senaryolar_changed
        )
        if imported_name:
            self.status_updated.emit(f"'{imported_name}' senaryosu içe aktarıldı.")
        else:
            self.status_updated.emit("Senaryo içe aktarılamadı. Dosya formatını kontrol edin.")