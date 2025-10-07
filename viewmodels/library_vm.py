# ew_platformasi/viewmodels/library_vm.py

from PySide6.QtCore import QObject, Signal, QSortFilterProxyModel, Qt
from core.data_manager import DataManager
from core.models import RadarTableModel, TeknikTableModel
from core.data_models import Radar, Teknik, Senaryo


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

        self._update_radars_model()
        self._update_teknikler_model()

    def _on_senaryolar_changed(self):
        """
        Senaryo verileri değiştiğinde (örn. yeni set yüklendiğinde) çağrılır.
        Bu viewmodel doğrudan bir senaryo listesi göstermese de, 'Faaliyet Geçmişi'
        gibi özelliklerin güncel veriye erişmesi için bu sinyali dinlemesi kritik öneme sahiptir.
        Metodun içi boş olabilir, önemli olan sinyal bağlantısının kurulmasıdır.
        """
        pass

    def _update_radars_model(self):
        self._radars_source_model.refresh_data(self._data_manager.radarlar)

    def _update_teknikler_model(self):
        self._teknikler_source_model.refresh_data(self._data_manager.teknikler)

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

    # --- BU FONKSİYON EKSİKTİ ---
    def item_exists(self, item_id: str, item_type: type) -> bool:
        """Verilen ID ve tipe sahip bir öğenin var olup olmadığını kontrol eder."""
        list_ref, _, _ = self._data_manager._get_list_ref(item_type)
        if list_ref is None:
            return False

        id_field = f"{item_type.__name__.lower()}_id"
        return any(getattr(item, id_field) == item_id for item in list_ref)
