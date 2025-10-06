# ew_platformasi/viewmodels/gorev_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import GorevTableModel
from core.data_models import Gorev, Senaryo


class GorevViewModel(QObject):
    status_updated = Signal(str)

    def __init__(self, data_manager: DataManager):
        super().__init__()
        self._data_manager = data_manager
        self._data_manager.status_updated.connect(self.status_updated)

        self._source_model = GorevTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self._source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self._data_manager.gorevler_changed.connect(self._update_model)
        self._update_model()

    def _update_model(self):
        self._source_model.refresh_data(self._data_manager.gorevler)

    def set_filter(self, text: str):
        self.proxy_model.setFilterFixedString(text)

    def get_item_from_proxy_index(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self._source_model.get_item_by_index(source_index)

    def get_senaryos_for_gorev(self, gorev: Gorev) -> list[Senaryo]:
        if not gorev: return []
        senaryo_map = {s.senaryo_id: s for s in self._data_manager.senaryolar}
        return [senaryo_map[sid] for sid in gorev.senaryo_id_list if sid in senaryo_map]

    def get_available_senaryos(self) -> list[Senaryo]:
        return self._data_manager.senaryolar

    def save_item(self, item: Gorev):
        self._data_manager.save_item(item)
        self.status_updated.emit(f"'{item.adi}' görevi kaydedildi.")

    def delete_item(self, item: Gorev):
        self._data_manager.delete_item_by_id(item.gorev_id, Gorev)
        self.status_updated.emit(f"'{item.adi}' görevi silindi.")

    def export_package(self, gorev_id: str, path: str):
        self._data_manager.export_gorev_package(gorev_id, path)

    def import_package(self, path: str):
        self._data_manager.import_gorev_package(path)