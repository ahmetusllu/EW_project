# ew_platformasi/ui/views/scenario_center_view.py

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
                               QLineEdit, QTableView, QHeaderView, QLabel, QPushButton,
                               QFileDialog, QMessageBox)
from viewmodels.scenario_vm import ScenarioViewModel


class ScenarioCenterView(QWidget):
    def __init__(self, view_model: ScenarioViewModel, parent=None):
        super().__init__(parent)
        self.vm = view_model
        self.current_scenario = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol Panel: Liste ve Filtre
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.search_box = QLineEdit(placeholderText="Senaryo adı, konum veya sonuçta ara...")
        self.table = QTableView()
        self.table.setModel(self.vm.proxy_model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.search_box)
        left_layout.addWidget(self.table)

        # Sağ Panel: Detaylar ve İşlemler
        right_panel = QGroupBox("Senaryo Detayları")
        right_layout = QVBoxLayout(right_panel)
        self.detail_labels = {}
        for key in ["adi", "tarih_iso", "konum", "amac", "radar_id", "teknik_id_list", "sonuc_nitel", "js_db",
                    "mesafe_km", "notlar"]:
            label_name = key.replace("_", " ").title()
            self.detail_labels[key] = QLabel("...")
            self.detail_labels[key].setWordWrap(True)
            form_row = QHBoxLayout()
            form_row.addWidget(QLabel(f"<b>{label_name}:</b>"), 1)
            form_row.addWidget(self.detail_labels[key], 3)
            right_layout.addLayout(form_row)
        right_layout.addStretch()

        button_layout = QHBoxLayout()
        self.btn_import = QPushButton("İçe Aktar", icon=qta.icon('fa5s.file-import'))
        self.btn_export = QPushButton("Dışa Aktar", icon=qta.icon('fa5s.file-export'))
        self.btn_delete = QPushButton("Sil", icon=qta.icon('fa5s.trash-alt'))
        button_layout.addWidget(self.btn_import)
        button_layout.addWidget(self.btn_export)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_delete)
        right_layout.addLayout(button_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        self._clear_details()

    def _connect_signals(self):
        self.search_box.textChanged.connect(self.vm.set_filter)
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.btn_export.clicked.connect(self._export_scenario)
        self.btn_import.clicked.connect(self._import_scenario)
        self.btn_delete.clicked.connect(self._delete_scenario)

    def _on_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            self._clear_details()
            return

        self.current_scenario = self.vm.get_item_from_proxy_index(indexes[0])
        if self.current_scenario:
            self._populate_details(self.current_scenario)

    def _populate_details(self, scenario):
        radar_map, teknik_map = self.vm.get_full_data_maps()
        for key, widget in self.detail_labels.items():
            value = getattr(scenario, key)
            if key == "radar_id":
                widget.setText(radar_map.get(value, "Bilinmiyor"))
            elif key == "teknik_id_list":
                names = [teknik_map.get(tid, "Bilinmiyor") for tid in value]
                widget.setText(", ".join(names))
            else:
                widget.setText(str(value or "N/A"))
        self.btn_export.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def _clear_details(self):
        self.current_scenario = None
        for widget in self.detail_labels.values():
            widget.setText("...")
        self.btn_export.setEnabled(False)
        self.btn_delete.setEnabled(False)

    def _export_scenario(self):
        if not self.current_scenario: return
        path, _ = QFileDialog.getSaveFileName(self, "Senaryo Dışa Aktar", f"{self.current_scenario.adi}.xml",
                                              "XML Dosyaları (*.xml)")
        if path:
            self.vm.export_scenario(self.current_scenario, path)

    def _import_scenario(self):
        path, _ = QFileDialog.getOpenFileName(self, "Senaryo İçe Aktar", "", "XML Dosyaları (*.xml)")
        if path:
            self.vm.import_scenarios(path)

    def _delete_scenario(self):
        if not self.current_scenario: return
        reply = QMessageBox.question(self, "Silme Onayı",
                                     f"'{self.current_scenario.adi}' senaryosunu silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            self.vm.delete_scenario(self.current_scenario)
            self._clear_details()